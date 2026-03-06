"""
validator.py
------------
Validates that scraped and cleaned content meets minimum quality requirements
before it is passed to the document processing pipeline.

Checks:
- Non-empty text (minimum character count)
- At least one expected field is present (e.g., "expense ratio", "exit load")
- Language detection (English only)
"""

from typing import Optional

MIN_CHAR_COUNT = 200

EXPECTED_KEYWORDS = [
    "expense ratio",
    "exit load",
    "sip",
    "riskometer",
    "benchmark",
    "lock-in",
    "nav",
    "scheme",
]


# ---------------------------------------------------------------------------
# TODO: Implement validation logic
# ---------------------------------------------------------------------------

class DocumentValidator:
    """Validates cleaned text content before chunking."""

    def validate(self, text: str, url: str) -> tuple[bool, Optional[str]]:
        """
        Returns (is_valid, reason_if_invalid).
        """
        raise NotImplementedError

    def _has_minimum_length(self, text: str) -> bool:
        raise NotImplementedError

    def _has_expected_keywords(self, text: str) -> bool:
        raise NotImplementedError
