"""Lightweight text normalization for display and word-cloud generation.

Sentiment is scored on the original comments, so this preprocessing deliberately
is not used as the input to sentiment classification (to preserve negations).
"""
from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for",
    "from", "had", "has", "have", "he", "her", "here", "hers", "him", "his",
    "how", "i", "if", "in", "into", "is", "it", "its", "me", "my", "of",
    "on", "or", "our", "ours", "she", "so", "than", "that", "the", "their",
    "them", "then", "there", "these", "they", "this", "those", "to", "too",
    "us", "was", "we", "were", "what", "when", "where", "which", "who", "why",
    "will", "with", "you", "your", "yours",
}


def clean(org_comments: list[str]) -> list[str]:
    """Normalize a list of comments while preserving list order and length."""
    cleaned: list[str] = []
    for comment in org_comments:
        if not isinstance(comment, str):
            cleaned.append("")
            continue
        tokens = [token.lower() for token in _TOKEN_RE.findall(comment)]
        tokens = [token for token in tokens if len(token) > 2 and token not in _STOP_WORDS]
        cleaned.append(" ".join(tokens))
    return cleaned
