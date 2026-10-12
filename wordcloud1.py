"""Word-cloud image generation with per-analysis output files."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wordcloud import STOPWORDS, WordCloud

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "static" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def create_wordcloud(clean_reviews: list[str], filename: str = "woc.png") -> str:
    """Create a word-cloud PNG under static/images and return its filename."""
    safe_filename = Path(filename).name
    if not safe_filename.lower().endswith(".png") or not re.fullmatch(r"[A-Za-z0-9_.-]+\.png", safe_filename):
        raise ValueError("Word-cloud filename must be a simple PNG filename.")
    text = " ".join(item.strip() for item in clean_reviews if isinstance(item, str) and item.strip())
    if not text:
        raise ValueError("There is no usable text from which to create a word cloud.")

    cloud = WordCloud(
        width=1400,
        height=800,
        stopwords=set(STOPWORDS),
        background_color="white",
        collocations=False,
        max_words=200,
    ).generate(text)
    output_path = IMAGES_DIR / safe_filename
    figure = plt.figure(figsize=(14, 8), facecolor="white")
    try:
        plt.imshow(cloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        figure.savefig(output_path, dpi=120, bbox_inches="tight", facecolor="white")
    finally:
        plt.close(figure)
    return safe_filename
