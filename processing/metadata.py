"""
metadata.py
-----------
Builds the standardised metadata schema for each chunk.

Metadata schema (per chunk):
{
    "chunk_id":      str,   # "{scheme-slug}-chunk-{index:03d}"
    "source_url":    str,   # original page URL
    "scheme_name":   str,   # e.g. "Mirae Asset Large Cap Fund"
    "amc":           str,   # e.g. "Mirae Asset"
    "page_type":     str,   # "fact_sheet" | "sid" | "help" | "amfi" | "sebi"
    "scraped_at":    str,   # ISO 8601 timestamp
    "chunk_index":   int,
    "total_chunks":  int,
    "language":      str    # "en"
}
"""

import datetime
from typing import Any


# ---------------------------------------------------------------------------
# TODO: Implement metadata builder
# ---------------------------------------------------------------------------

class MetadataBuilder:
    """Constructs per-chunk metadata dicts from source page info."""

    def build(
        self,
        source_url: str,
        scheme_name: str,
        amc: str,
        page_type: str,
        chunk_index: int,
        total_chunks: int,
        scraped_at: str | None = None,
    ) -> dict[str, Any]:
        """Build and return a metadata dict for a single chunk."""
        raise NotImplementedError

    def _slug(self, scheme_name: str) -> str:
        """Convert scheme name to a URL-safe slug."""
        raise NotImplementedError
