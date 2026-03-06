"""
validator.py
------------
Validates that scraped and cleaned content meets minimum quality requirements
before it is passed to the document processing pipeline.

Checks:
1. Non-empty text (minimum character count)
2. At least one mutual-fund keyword present
3. Not an error page (404, access denied patterns)
"""

import re
from typing import Optional

MIN_CHAR_COUNT = 200  # Minimum characters for a document to be useful

# At least one of these must appear (case-insensitive) for the page to be relevant
EXPECTED_KEYWORDS = [
    "expense ratio",
    "exit load",
    "sip",
    "riskometer",
    "benchmark",
    "lock-in",
    "lock in",
    "nav",
    "scheme",
    "mutual fund",
    "amc",
    "amfi",
    "sebi",
    "elss",
    "investment",
    "systematic investment",
    "statement",
    "portfolio",
]

# Patterns that indicate the page is an error / access-denied page
ERROR_PATTERNS = [
    r"404\s+not found",
    r"page not found",
    r"access denied",
    r"403 forbidden",
    r"this page (does not exist|is unavailable)",
    r"enable javascript to view",
]


class DocumentValidator:
    """Validates cleaned text content before chunking."""

    def validate(self, text: str, url: str) -> tuple[bool, Optional[str]]:
        """
        Returns (is_valid, reason_if_invalid).

        Args:
            text: Cleaned plain text from the page.
            url:  Source URL (used in error messages).

        Returns:
            (True, None) if valid.
            (False, "<reason>") if invalid.
        """
        if not self._has_minimum_length(text):
            return False, (
                f"Too short ({len(text)} chars < {MIN_CHAR_COUNT} required): {url}"
            )

        if self._is_error_page(text):
            return False, f"Error/access-denied page detected: {url}"

        if not self._has_expected_keywords(text):
            return False, (
                f"No mutual-fund keywords found — likely off-topic page: {url}"
            )

        return True, None

    def _has_minimum_length(self, text: str) -> bool:
        """Check document exceeds the minimum character threshold."""
        return len(text.strip()) >= MIN_CHAR_COUNT

    def _is_error_page(self, text: str) -> bool:
        """Detect HTTP error or access-denied pages."""
        lower = text.lower()
        return any(re.search(p, lower) for p in ERROR_PATTERNS)

    def _has_expected_keywords(self, text: str) -> bool:
        """Ensure at least one mutual-fund keyword is present."""
        lower = text.lower()
        return any(kw in lower for kw in EXPECTED_KEYWORDS)
