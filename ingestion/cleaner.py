"""
cleaner.py
----------
Converts raw HTML (or PDF-extracted text) into clean, normalised plain text.

Steps performed:
1. Remove navigation, footer, script, style, and ad HTML tags
2. Strip all remaining HTML tags
3. Collapse multiple whitespace / newlines
4. Normalise Unicode (NFKC) — handles ₹, %, — correctly
5. Remove boilerplate phrases (cookie notices, subscription banners, etc.)
"""

import re
import unicodedata
from bs4 import BeautifulSoup

# Phrases to strip from extracted text (case-insensitive)
BOILERPLATE_PHRASES = [
    "cookie policy",
    "subscribe to our newsletter",
    "accept all cookies",
    "privacy policy",
    "terms and conditions",
]

# Tags whose entire subtree should be removed
REMOVABLE_TAGS = ["nav", "footer", "script", "style", "header", "aside", "ads"]


# ---------------------------------------------------------------------------
# TODO: Implement HTML cleaning pipeline
# ---------------------------------------------------------------------------

class HTMLCleaner:
    """Cleans raw HTML into plain text suitable for chunking."""

    def clean(self, html: str) -> str:
        """
        Main entry point. Accepts raw HTML string, returns clean text.
        """
        raise NotImplementedError

    def _remove_tags(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted HTML tag subtrees in-place."""
        raise NotImplementedError

    def _strip_boilerplate(self, text: str) -> str:
        """Remove known boilerplate phrases from text."""
        raise NotImplementedError

    def _normalise(self, text: str) -> str:
        """NFKC Unicode normalisation + whitespace collapse."""
        raise NotImplementedError
