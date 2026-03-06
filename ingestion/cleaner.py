"""
cleaner.py
----------
Converts raw HTML into clean, normalised plain text.

Steps:
1. Remove noise tags (nav, footer, script, style, header, aside)
2. Extract <title> for use as document title
3. Strip all remaining HTML tags
4. Collapse multiple whitespace / newlines
5. Normalise Unicode (NFKC) — handles ₹, %, — correctly
6. Remove boilerplate phrases (cookie notices, subscription banners, etc.)
"""

import re
import unicodedata
from bs4 import BeautifulSoup

# Phrases to strip line-by-line (case-insensitive substring match)
BOILERPLATE_PHRASES = [
    "cookie policy",
    "subscribe to our newsletter",
    "accept all cookies",
    "privacy policy",
    "terms and conditions",
    "all rights reserved",
    "javascript is required",
    "enable javascript",
    "loading...",
    "please wait",
]

# Tags whose entire subtree should be removed
REMOVABLE_TAGS = [
    "nav", "footer", "script", "style", "header",
    "aside", "noscript", "iframe", "form", "button",
    "svg", "img", "figure", "ads", "advertisement",
]


class HTMLCleaner:
    """Cleans raw HTML into plain text suitable for chunking."""

    def clean(self, html: str) -> tuple[str, str]:
        """
        Main entry point.

        Args:
            html: Raw HTML string.

        Returns:
            (title, clean_text) — both as plain strings.
        """
        soup = BeautifulSoup(html, "html.parser")
        title = self._extract_title(soup)
        soup = self._remove_tags(soup)
        raw_text = soup.get_text(separator="\n")
        text = self._normalise(raw_text)
        text = self._strip_boilerplate(text)
        return title, text

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page <title> or first <h1>."""
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return ""

    def _remove_tags(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted HTML tag subtrees in-place."""
        for tag in REMOVABLE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
        return soup

    def _strip_boilerplate(self, text: str) -> str:
        """Remove lines containing known boilerplate phrases."""
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            lower = line.lower()
            if not any(phrase in lower for phrase in BOILERPLATE_PHRASES):
                cleaned.append(line)
        return "\n".join(cleaned)

    def _normalise(self, text: str) -> str:
        """NFKC Unicode normalisation + whitespace collapse."""
        # Unicode normalise (handles ₹, —, etc.)
        text = unicodedata.normalize("NFKC", text)
        # Collapse 3+ consecutive newlines → 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple spaces/tabs on a single line
        text = re.sub(r"[ \t]+", " ", text)
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.splitlines()]
        # Remove completely empty lines that are repeated
        cleaned = []
        prev_blank = False
        for line in lines:
            if line == "":
                if not prev_blank:
                    cleaned.append(line)
                prev_blank = True
            else:
                cleaned.append(line)
                prev_blank = False
        return "\n".join(cleaned).strip()
