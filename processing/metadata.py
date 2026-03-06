"""
metadata.py
-----------
Builds the standardised per-chunk metadata dict used across:
  - processing (chunk assembly)
  - embeddings (stored in Chroma)
  - retrieval  (returned with top-k results)
  - LLM layer  (citation source_url extraction)

Metadata schema (all values must be str | int | float | bool for Chroma):
{
    "chunk_id":     str,   # "{scheme-slug}-chunk-{index:03d}"
    "source_url":   str,   # original page URL
    "title":        str,   # page title (from scraper)
    "scheme_name":  str,   # e.g. "Mirae Asset Large Cap Fund" (or "")
    "amc":          str,   # e.g. "Mirae Asset" (or "")
    "page_type":    str,   # "fund_detail" | "amc_fact_sheet" | "amfi" | "sebi"
    "scraped_at":   str,   # ISO 8601 UTC timestamp
    "chunk_index":  int,   # 0-based position within the source document
    "total_chunks": int,   # total chunks from this source document
    "language":     str    # "en"
}
"""

import re
from datetime import datetime, timezone
from typing import Any


class MetadataBuilder:
    """Constructs per-chunk metadata dicts from source page info."""

    def build(
        self,
        source_url:  str,
        title:       str,
        scheme_name: str | None,
        amc:         str | None,
        page_type:   str,
        chunk_index: int,
        total_chunks: int,
        scraped_at:  str | None = None,
    ) -> dict[str, Any]:
        """
        Build and return a metadata dict for a single chunk.

        Args:
            source_url:   Full URL of the source page.
            title:        Page title extracted by the scraper.
            scheme_name:  Mutual fund scheme name, or None for general pages.
            amc:          AMC name, or None for non-AMC sources.
            page_type:    Category label for the source page.
            chunk_index:  0-based position of this chunk within its document.
            total_chunks: Total number of chunks from this document.
            scraped_at:   ISO8601 timestamp; defaults to now (UTC) if None.

        Returns:
            Metadata dict with all Chroma-compatible value types.
        """
        slug = self._slug(scheme_name or page_type)
        chunk_id = f"{slug}-chunk-{chunk_index:03d}"

        return {
            "chunk_id":     chunk_id,
            "source_url":   source_url,
            "title":        title or "",
            "scheme_name":  scheme_name or "",
            "amc":          amc or "",
            "page_type":    page_type,
            "scraped_at":   scraped_at or datetime.now(timezone.utc).isoformat(),
            "chunk_index":  chunk_index,
            "total_chunks": total_chunks,
            "language":     "en",
        }

    def _slug(self, name: str) -> str:
        """Convert a scheme name or page type to a URL-safe lowercase slug."""
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)   # replace non-alphanumeric with -
        slug = slug.strip("-")                      # remove leading/trailing dashes
        return slug
