"""Flask app for YouTube comment sentiment analysis.

Authentication uses a local SQLite database by default so the app works without
an external MongoDB service. Optional email delivery is enabled through env vars.
"""
from __future__ import annotations

import json
import logging
from contextlib import contextmanager
import os
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash

from preprocessing import clean
from scraper import YouTubeScraperError, returnytcomments
from sentiment import returnsentiment
from wordcloud1 import create_wordcloud

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
INSTANCE_DIR = BASE_DIR / "instance"
ANALYSES_DIR = INSTANCE_DIR / "analyses"
IMAGES_DIR = BASE_DIR / "static" / "images"
DB_PATH = Path(os.environ.get("APP_DB_PATH", str(INSTANCE_DIR / "users.sqlite3")))

INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, instance_path=str(INSTANCE_DIR))
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or os.urandom(32),
    SEND_FILE_MAX_AGE_DEFAULT=0,
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT", "587")),
    MAIL_USE_TLS=os.environ.get("MAIL_USE_TLS", "true").lower() in {"1", "true", "yes"},
    MAIL_USE_SSL=os.environ.get("MAIL_USE_SSL", "false").lower() in {"1", "true", "yes"},
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
    MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER") or os.environ.get("MAIL_USERNAME") or None,
)
mail = Mail(app)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


@contextmanager
def get_db():
    """Yield a configured SQLite connection and always close it afterward."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        connection.commit()
        yield connection
    finally:
        connection.close()


def analysis_path(analysis_id: str) -> Path | None:
    """Resolve a UUID-only analysis ID to a file path, rejecting arbitrary paths."""
    try:
        safe_id = str(uuid.UUID(analysis_id))
    except (ValueError, TypeError, AttributeError):
        return None
    return ANALYSES_DIR / f"{safe_id}.json"


def load_current_analysis() -> dict[str, Any] | None:
    analysis_id = session.get("analysis_id")
    if not analysis_id:
        return None
    path = analysis_path(analysis_id)
    if path is None or not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Could not load analysis result")
        return None


def save_analysis(analysis_id: str, data: dict[str, Any]) -> None:
    path = analysis_path(analysis_id)
    if path is None:
        raise ValueError("Invalid analysis ID")
    temporary_path = path.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
    temporary_path.replace(path)


def valid_email(value: str) -> bool:
    """Small sanity check for optional email input; SMTP remains the final check."""
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value or ""))


def send_email(recipient: str, result_data: dict[str, Any]) -> tuple[bool, str]:
    """Email a short summary if SMTP settings are configured; never break analysis."""
    if not recipient:
        return False, ""
    if not valid_email(recipient):
        return False, "The email address does not look valid, so no email was sent."
    if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
        return False, "Analysis completed. Email delivery is not configured on this installation."

    try:
        summary = (
            f"YouTube comment sentiment analysis completed.\n\n"
            f"Comments analyzed: {result_data['n']}\n"
            f"Positive: {result_data['np']}\n"
            f"Neutral: {result_data['nne']}\n"
            f"Negative: {result_data['nn']}\n"
        )
        message = Message(
            subject="YouTube Comment Sentiment Analysis Results",
            recipients=[recipient],
            body=summary,
        )
        mail.send(message)
        return True, f"A summary email was sent to {recipient}."
    except Exception:
        app.logger.exception("Email delivery failed")
        return False, "Analysis completed, but the summary email could not be sent."


@app.route("/")
def index():
    if session.get("username"):
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("pass") or ""
    if not username or not password:
        return render_template("index.html", error="Enter both username and password."), 400

    try:
        with get_db() as connection:
            user = connection.execute(
                "SELECT username, password_hash FROM users WHERE username = ?", (username,)
            ).fetchone()
    except sqlite3.Error:
        app.logger.exception("Database error during login")
        return render_template("index.html", error="The local user database could not be opened."), 500

    if user and check_password_hash(user["password_hash"], password):
        session.clear()
        session["username"] = username
        return redirect(url_for("home"))
    return render_template("index.html", error="Invalid username or password."), 401


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("pass") or ""
    if len(username) < 3 or len(username) > 80:
        return render_template("register.html", error="Username must be between 3 and 80 characters."), 400
    if len(password) < 8:
        return render_template("register.html", error="Password must contain at least 8 characters."), 400

    try:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            connection.commit()
    except sqlite3.IntegrityError:
        return render_template("register.html", error="That username is already registered."), 409
    except sqlite3.Error:
        app.logger.exception("Database error during registration")
        return render_template("register.html", error="Could not create the account. Please try again."), 500

    session.clear()
    session["username"] = username
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/home")
def home():
    if not session.get("username"):
        return redirect(url_for("index"))
    return render_template("home.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/results", methods=["GET", "POST"])
def result():
    if not session.get("username"):
        return redirect(url_for("index"))

    # GET displays the latest saved analysis; POST starts a new one.
    if request.method == "GET":
        previous = load_current_analysis()
        if not previous:
            flash("Run a YouTube analysis first to view the results.", "warning")
            return redirect(url_for("home"))
        return render_template("result.html", **previous)

    video_url = (request.form.get("url") or "").strip()
    recipient_email = (request.form.get("email") or "").strip()
    if not video_url:
        return render_template("home.html", error="Enter a YouTube video URL."), 400
    if recipient_email and not valid_email(recipient_email):
        return render_template("home.html", error="Enter a valid email address or leave the email field blank."), 400

    try:
        scraped_comments = returnytcomments(video_url,max_comments=200,headless=False)
    except ValueError as exc:
        return render_template("home.html", error=str(exc)), 400
    except YouTubeScraperError as exc:
        app.logger.warning("YouTube comment extraction did not succeed: %s", exc)
        return render_template("home.html", error=str(exc)), 502
    except Exception:
        app.logger.exception("Unexpected YouTube scraping failure")
        return render_template(
            "home.html",
            error=("An unexpected scraping error occurred. Check the terminal running app.py for details."),
        ), 502

    # Keep the original text and cleaned text aligned for every result row.
    comments: list[str] = []
    for item in scraped_comments:
        if not isinstance(item, str):
            continue
        original = " ".join(item.split()).strip()
        if 1 < len(original) <= 1000:
            comments.append(original)

    if not comments:
        return render_template(
            "home.html",
            error="The scraper returned comments, but none contained enough text to analyze. Try another video or check its comment text.",
        ), 422

    cleaned_comments = clean(comments)
    data_rows: list[dict[str, Any]] = []
    positive = neutral = negative = 0

    for original, cleaned_text in zip(comments, cleaned_comments):
        # Classify the original text so preprocessing cannot remove negation words.
        score, label = returnsentiment(original)
        label_upper = label.upper()
        if label_upper == "POSITIVE":
            positive += 1
        elif label_upper == "NEGATIVE":
            negative += 1
        else:
            label_upper = "NEUTRAL"
            neutral += 1

        data_rows.append({
            "sent": label_upper,
            "clean_comment": cleaned_text,
            "org_comment": original,
            "score": round(float(score), 4),
        })

    analysis_id = str(uuid.uuid4())
    wordcloud_file = None
    try:
        # Use a unique filename per analysis to avoid one user's word cloud overwriting another's.
        useful_cleaned = [text for text in cleaned_comments if text and text.strip()]
        if useful_cleaned:
            wordcloud_file = create_wordcloud(useful_cleaned, filename=f"woc_{analysis_id}.png")
    except Exception:
        app.logger.exception("Word cloud generation failed; continuing without a word cloud")

    result_data = {
        "analysis_id": analysis_id,
        "username": session["username"],
        "n": len(data_rows),
        "nn": negative,
        "np": positive,
        "nne": neutral,
        "dic": data_rows,
        "wordcloud_file": wordcloud_file,
        "video_url": video_url,
    }
    sent_ok, email_notice = send_email(recipient_email, result_data)
    result_data["email_notice"] = email_notice
    result_data["email_sent"] = sent_ok

    try:
        save_analysis(analysis_id, result_data)
    except OSError:
        app.logger.exception("Could not save analysis results")
        return render_template("home.html", error="The analysis completed, but the results could not be saved."), 500

    session["analysis_id"] = analysis_id
    return render_template("result.html", **result_data)


@app.route("/wc")
def wc():
    if not session.get("username"):
        return redirect(url_for("index"))
    data = load_current_analysis()
    if not data:
        flash("Run a YouTube analysis first to view its word cloud.", "warning")
        return redirect(url_for("home"))
    wordcloud_url = None
    if data.get("wordcloud_file"):
        wordcloud_url = url_for("static", filename=f"images/{data['wordcloud_file']}")
    return render_template("wc.html", wordcloud_url=wordcloud_url)


@app.route("/visualization")
def visualization():
    if not session.get("username"):
        return redirect(url_for("index"))
    data = load_current_analysis()
    if not data:
        flash("Run a YouTube analysis first to view its visualization.", "warning")
        return redirect(url_for("home"))
    return render_template("visualization.html", **data)


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", message="The page you requested could not be found."), 404


if __name__ == "__main__":
    # Debug mode is intentionally off by default. Set FLASK_DEBUG=1 for local debugging.
    app.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"},
    )
