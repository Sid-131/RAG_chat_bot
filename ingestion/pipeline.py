"""
pipeline.py
-----------
Orchestrates the full ingestion pipeline:
  1. Load URL list from data/sources.json
  2. Scrape each URL (async)
  3. Clean HTML → plain text
  4. Validate content quality
  5. Save clean text + JSON metadata sidecar to data/raw/

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
    """
    raise NotImplementedError


if __name__ == "__main__":
    asyncio.run(run_pipeline())
