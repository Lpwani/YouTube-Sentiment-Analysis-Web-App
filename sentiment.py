"""Three-class sentiment scoring using NLTK VADER with an offline fallback.

VADER returns a compound polarity score in [-1, 1]. Scores >= 0.05 are
Positive, <= -0.05 are Negative, and values in between are Neutral."""
from __future__ import annotations

import logging
import re

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

LOGGER = logging.getLogger(__name__)
_ANALYZER = None


def _load_analyzer():
    try:
        return SentimentIntensityAnalyzer()
    except LookupError:
        try:
            if nltk.download("vader_lexicon", quiet=True):
                return SentimentIntensityAnalyzer()
        except Exception:
            LOGGER.warning("Could not download the VADER lexicon; using the lightweight fallback scorer.")
        LOGGER.warning("VADER lexicon is unavailable; using a lightweight fallback sentiment scorer.")
        return None


_ANALYZER = _load_analyzer()
_POSITIVE_WORDS = {
    "amazing", "awesome", "best", "brilliant", "enjoy", "excellent",
    "fantastic", "fun", "good", "great", "happy", "love", "loved",
    "nice", "perfect", "thank", "thanks", "wonderful", "wow", "beautiful",
}
_NEGATIVE_WORDS = {
    "awful", "bad", "boring", "disappointing", "hate", "hated", "horrible",
    "poor", "terrible", "trash", "ugly", "worst", "wrong", "annoying",
}
_TOKEN_RE = re.compile(r"[a-zA-Z]+")


def _fallback_compound(text: str) -> float:
    tokens = [token.lower() for token in _TOKEN_RE.findall(text)]
    if not tokens:
        return 0.0
    positive = sum(token in _POSITIVE_WORDS for token in tokens)
    negative = sum(token in _NEGATIVE_WORDS for token in tokens)
    polarity = positive - negative
    if polarity == 0:
        return 0.0
    # Deliberately conservative fallback, not a replacement for VADER.
    return max(-1.0, min(1.0, polarity / max(2.0, len(tokens) ** 0.5)))


def returnsentiment(text: str) -> tuple[float, str]:
    """Return (compound score, label) where label is Positive, Neutral or Negative."""
    if not isinstance(text, str) or not text.strip():
        return 0.0, "Neutral"
    if _ANALYZER is not None:
        compound = float(_ANALYZER.polarity_scores(text)["compound"])
    else:
        compound = _fallback_compound(text)
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    return compound, label
