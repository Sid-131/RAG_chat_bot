"""
pipeline.py
-----------
Orchestrates the full ingestion pipeline:
  1. Load URL list from data/sources.json
  2. Scrape each URL:
     - Playwright (headless Chromium) for Groww pages (React/Next.js)
     - httpx for static pages (AMC, AMFI, SEBI, CAMS)
  3. Clean HTML → plain text
  4. Validate content quality
  5. Save clean text + JSON metadata sidecar to data/raw/

sources.json schema (per entry):
  { "url": str, "scheme_name": str|null, "amc": str|null,
    "page_type": str, "source": str, "fields": list[str] }

The "source" field drives scraper mode:
  "groww" / "groww_help"  → Playwright
  everything else          → httpx

Usage:
    python -m ingestion.pipeline
"""

import asyncio
import json
from pathlib import Path

from ingestion.scraper import Scraper
from ingestion.cleaner import HTMLCleaner
from ingestion.validator import DocumentValidator

SOURCES_PATH = Path("data/sources.json")
RAW_OUTPUT_DIR = Path("data/raw")


# ---------------------------------------------------------------------------
# TODO: Implement pipeline orchestrator
# ---------------------------------------------------------------------------

async def run_pipeline():
    """
    Main async entry point. Reads sources.json, runs scrape→clean→validate
    for each URL, and writes outputs to data/raw/.

    For each source entry:
      1. Passes source["source"] as source_type to Scraper.fetch()
      2. Passes cleaned text to HTMLCleaner.clean()
      3. Validates with DocumentValidator.validate()
      4. Saves {slug}.txt + {slug}.json to data/raw/
    """
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))

    async with Scraper() as scraper:
        cleaner = HTMLCleaner()
        validator = DocumentValidator()

        for entry in sources:
            url = entry["url"]
            source_type = entry.get("source", "static")
            # TODO: implement fetch → clean → validate → save
            raise NotImplementedError


if __name__ == "__main__":
    asyncio.run(run_pipeline())

