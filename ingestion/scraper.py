"""
scraper.py
----------
Async HTTP fetcher for official mutual fund public pages.

Responsibilities:
- Fetch page HTML given a URL
- Enforce rate limiting (1 req/sec per domain, random jitter)
- Retry with exponential backoff on 5xx / timeout (max 3 retries)
- Respect robots.txt for each domain
- Handle PDF downloads (returns raw bytes for pdfminer to parse)
"""

import asyncio
import random
import time
from pathlib import Path
from typing import Optional
import httpx
from urllib.robotparser import RobotFileParser


# ---------------------------------------------------------------------------
# TODO: Implement async page fetcher
# ---------------------------------------------------------------------------

class Scraper:
    """Async scraper with rate-limiting and retry logic."""

    def __init__(self, rate_limit: float = 1.0, max_retries: int = 3):
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._domain_last_request: dict[str, float] = {}

    async def fetch(self, url: str) -> Optional[bytes]:
        """Fetch content from a URL. Returns raw bytes or None on failure."""
        raise NotImplementedError

    def _is_allowed(self, url: str) -> bool:
        """Check robots.txt compliance for the given URL."""
        raise NotImplementedError

    async def _throttle(self, domain: str) -> None:
        """Enforce per-domain rate limiting with random jitter."""
        raise NotImplementedError
