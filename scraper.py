"""Best-effort scraper for public YouTube video comments.

YouTube changes its DOM periodically, so this module supports both the older
``ytd-comment-thread-renderer`` markup and the newer ``ytd-comment-view-model``
markup. It reports blocked/changed pages instead of silently treating every
empty extraction as a video with no comments.
"""
from __future__ import annotations

import time
from urllib.parse import parse_qs, urlparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class YouTubeScraperError(RuntimeError):
    """Raised when a YouTube page cannot be read as a comments page."""


# Search newer and older YouTube structures. The same comment may match more
# than one selector, so extracted text is deduplicated below.
COMMENT_SELECTORS = (
    "ytd-comment-view-model#content-text",
    "ytd-comment-view-model #content-text",
    "ytd-comment-thread-renderer #content-text",
    "ytd-comments #content-text",
    "#comments #content-text",
)
COMMENT_SELECTOR = ", ".join(COMMENT_SELECTORS)


def validate_youtube_url(url: str) -> str:
    """Validate a YouTube host and ensure the URL contains a video ID."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Enter a YouTube video URL.")

    candidate = url.strip()
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    allowed_hosts = {
        "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
        "www.youtube-nocookie.com",
    }
    if parsed.scheme not in {"http", "https"} or host not in allowed_hosts:
        raise ValueError("Please enter a valid YouTube video URL (youtube.com or youtu.be).")

    video_id = None
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/", "/live/")):
            parts = parsed.path.strip("/").split("/")
            video_id = parts[1] if len(parts) > 1 else None
    elif host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif host == "www.youtube-nocookie.com" and parsed.path.startswith("/embed/"):
        parts = parsed.path.strip("/").split("/")
        video_id = parts[1] if len(parts) > 1 else None

    if not video_id or not (6 <= len(video_id) <= 20):
        raise ValueError("That URL does not look like a YouTube video URL. Paste a video/watch or youtu.be link.")
    return candidate


def _make_driver(headless: bool = True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1365,1000")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _maybe_handle_consent(driver) -> None:
    """Click a visible, explicit YouTube consent action if a consent screen appears."""
    try:
        current = (driver.current_url or "").lower()
        body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
        if "consent.youtube.com" not in current and "before you continue to youtube" not in body:
            return
        # Prefer a privacy-preserving choice. Only click buttons with exact labels.
        for button in driver.find_elements(By.CSS_SELECTOR, "button"):
            label = " ".join((button.text or "").split()).strip().lower()
            if label in {"reject all", "reject non-essential cookies", "i agree", "agree"}:
                try:
                    button.click()
                    time.sleep(1.5)
                    return
                except WebDriverException:
                    continue
    except WebDriverException:
        return


def _extract_visible_comments(driver) -> list[str]:
    """Read comments matched by any known current/legacy DOM selector."""
    texts: list[str] = []
    seen: set[str] = set()
    for element in driver.find_elements(By.CSS_SELECTOR, COMMENT_SELECTOR):
        try:
            text = driver.execute_script(
                "return (arguments[0].innerText || arguments[0].textContent || '').trim();",
                element,
            )
        except WebDriverException:
            text = element.text
        text = " ".join(str(text or "").split()).strip()
        if text and text not in seen:
            seen.add(text)
            texts.append(text)
    return texts


def _explain_empty_page(driver) -> str:
    """Infer a useful failure explanation from visible page text, not guesses."""
    try:
        body_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    except WebDriverException:
        body_text = ""
    try:
        page_url = (driver.current_url or "").lower()
    except WebDriverException:
        page_url = ""

    if "comments are turned off" in body_text or "comments are disabled" in body_text:
        return "YouTube says comments are turned off for this video. Try another public video with comments enabled."
    if ("confirm you're not a bot" in body_text or "confirm you’re not a bot" in body_text
            or "unusual traffic" in body_text or "captcha" in page_url or "/sorry/" in page_url):
        return (
            "YouTube blocked this automated browser session. Open the video normally in Chrome to check access, "
            "then try again later. The app does not bypass YouTube's access restrictions."
        )
    if "before you continue to youtube" in body_text or "consent.youtube.com" in page_url:
        return "YouTube is showing a consent page that the scraper could not dismiss. Open YouTube in Chrome and complete the consent prompt, then retry."
    if "sign in to confirm your age" in body_text or "age-restricted" in body_text:
        return "This video appears to require sign-in or age verification, so its comments cannot be read by this scraper."
    return (
        "The video page opened, but no comments were found using the known YouTube page layouts. "
        "YouTube may have changed its page structure or restricted automated access. Check that comments are visible "
        "when you open this same video in Chrome."
    )


def returnytcomments(url: str, max_comments: int = 200, headless: bool = False) -> list[str]:
    """Return up to ``max_comments`` distinct comment texts from a public video.

    This collects comments exposed in the public page. It does not bypass login,
    age, region, consent, CAPTCHA, or other YouTube access restrictions.
    """
    video_url = validate_youtube_url(url)
    max_comments = max(1, min(int(max_comments), 1000))
    found: list[str] = []
    seen: set[str] = set()

    try:
        with _make_driver(headless=headless) as driver:
            driver.set_page_load_timeout(45)
            driver.get(video_url)
            WebDriverWait(driver, 25).until(
                lambda current_driver: current_driver.find_elements(By.TAG_NAME, "body")
            )
            time.sleep(1.5)
            _maybe_handle_consent(driver)

            # The comment container can exist before it has loaded its contents.
            # Scroll it into view rather than assuming the first page scroll reaches it.
            for _ in range(18):
                sections = driver.find_elements(
                    By.CSS_SELECTOR,
                    "ytd-comments, #comments, ytd-item-section-renderer[section-identifier='comment-item-section']",
                )
                if sections:
                    try:
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'start', behavior: 'instant'});",
                            sections[0],
                        )
                    except WebDriverException:
                        driver.execute_script("window.scrollBy(0, 800);")
                    break
                driver.execute_script("window.scrollBy(0, Math.max(window.innerHeight, 700));")
                time.sleep(0.6)

            # Try waiting for either DOM layout. Do not fail just because one
            # particular selector is absent; the scroll loop below still runs.
            try:
                WebDriverWait(driver, 10).until(
                    lambda current_driver: bool(_extract_visible_comments(current_driver))
                    or bool(current_driver.find_elements(By.CSS_SELECTOR, "ytd-comments, #comments"))
                )
            except TimeoutException:
                pass

            no_growth_rounds = 0
            previous_count = 0
            empty_rounds = 0
            for _ in range(40):
                current_comments = _extract_visible_comments(driver)
                for text in current_comments:
                    if text not in seen:
                        seen.add(text)
                        found.append(text)
                        if len(found) >= max_comments:
                            return found[:max_comments]

                if len(found) == previous_count:
                    no_growth_rounds += 1
                else:
                    no_growth_rounds = 0
                previous_count = len(found)

                if not current_comments:
                    empty_rounds += 1
                else:
                    empty_rounds = 0

                if no_growth_rounds >= 5 and found:
                    break
                if empty_rounds >= 12:
                    break

                # Scrolling the final loaded comment reliably triggers YouTube's
                # lazy-loader; if none exists yet, continue down the main page.
                elements = driver.find_elements(By.CSS_SELECTOR, COMMENT_SELECTOR)
                if elements:
                    try:
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'end', behavior: 'instant'});",
                            elements[-1],
                        )
                    except WebDriverException:
                        driver.execute_script("window.scrollBy(0, Math.max(window.innerHeight, 700));")
                else:
                    driver.execute_script("window.scrollBy(0, Math.max(window.innerHeight, 700));")
                time.sleep(1.0)

            if found:
                return found[:max_comments]
            raise YouTubeScraperError(_explain_empty_page(driver))

    except ValueError:
        raise
    except YouTubeScraperError:
        raise
    except (WebDriverException, TimeoutException) as exc:
        raise YouTubeScraperError(
            "Could not open or read the YouTube page. Check your internet connection, Chrome installation, "
            "and that webdriver-manager can download a compatible ChromeDriver."
        ) from exc
