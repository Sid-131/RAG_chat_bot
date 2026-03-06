"""
pipeline.py
-----------
Orchestrates the full ingestion pipeline:

  1. Load URL list from data/sources.json
  2. Scrape each URL:
       - Playwright (headless Chromium) for Groww pages (React/Next.js)
       - httpx for static pages (AMC, AMFI, SEBI, CAMS)
  3. Clean HTML → plain text  (HTMLCleaner)
  4. Validate content quality  (DocumentValidator)
  5. Save output to data/raw/<slug>.json

Output JSON schema per document:
  {
    "url":        "<source URL>",
    "title":      "<page title or empty string>",
    "content":    "<clean plain text>",
    "scheme_name": "<scheme name or null>",
    "amc":        "<AMC name or null>",
    "page_type":  "<fund_detail | amc_fact_sheet | amfi | sebi | ...>",
    "source":     "<groww | groww_help | amc | amfi | sebi | cams>",
    "scraped_at": "<ISO-8601 UTC timestamp>"
  }

Usage:
    python -m ingestion.pipeline
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from ingestion.scraper import Scraper, url_to_slug
from ingestion.cleaner import HTMLCleaner
from ingestion.validator import DocumentValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

SOURCES_PATH   = Path("data/sources.json")
RAW_OUTPUT_DIR = Path("data/raw")


async def run_pipeline(sources_path: Path = SOURCES_PATH) -> list[dict]:
    """
    Main async entry-point. Reads sources.json, runs scrape→clean→validate
    for each URL, and writes outputs to data/raw/.

    Returns:
        List of successfully saved document dicts.
    """
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not sources_path.exists():
        logger.error("sources.json not found at %s", sources_path)
        return []

    sources: list[dict] = json.loads(sources_path.read_text(encoding="utf-8"))
    logger.info("Loaded %d source URLs from %s", len(sources), sources_path)

    cleaner   = HTMLCleaner()
    validator = DocumentValidator()
    saved_docs: list[dict] = []

    async with Scraper() as scraper:
        for i, entry in enumerate(sources, start=1):
            url         = entry["url"]
            source_type = entry.get("source", "static")
            logger.info("[%d/%d] Fetching %s (type=%s)", i, len(sources), url, source_type)

            # ── Step 1: Fetch ────────────────────────────────────────────────
            html = await scraper.fetch(url, source_type=source_type)
            if not html:
                logger.warning("  ✗ Skipped (fetch failed): %s", url)
                continue

            # ── Step 2: Clean ────────────────────────────────────────────────
            title, clean_text = cleaner.clean(html)

            # ── Step 3: Validate ─────────────────────────────────────────────
            is_valid, reason = validator.validate(clean_text, url)
            if not is_valid:
                logger.warning("  ✗ Skipped (validation failed): %s", reason)
                continue

            # ── Step 4: Build output document ────────────────────────────────
            doc = {
                "url":         url,
                "title":       title,
                "content":     clean_text,
                "scheme_name": entry.get("scheme_name"),
                "amc":         entry.get("amc"),
                "page_type":   entry.get("page_type", "unknown"),
                "source":      source_type,
                "scraped_at":  datetime.now(timezone.utc).isoformat(),
            }

            # ── Step 5: Save to disk ─────────────────────────────────────────
            slug      = url_to_slug(url)
            out_path  = RAW_OUTPUT_DIR / f"{slug}.json"
            out_path.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info("  ✓ Saved: %s (%d chars)", out_path.name, len(clean_text))
            saved_docs.append(doc)

    logger.info(
        "Pipeline complete — %d/%d pages saved to %s",
        len(saved_docs), len(sources), RAW_OUTPUT_DIR,
    )
    return saved_docs


if __name__ == "__main__":
    asyncio.run(run_pipeline())
