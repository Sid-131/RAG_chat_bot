"""
scraper.py
----------
Async scraper that handles both:
  - JavaScript-rendered pages (Groww fund pages — React/Next.js)
    → Uses Playwright (headless Chromium) to wait for dynamic content
  - Static HTML pages (AMC websites, AMFI, SEBI)
    → Uses httpx for fast, lightweight fetching

Groww pages (groww.in) require Playwright because:
  - NAV, Expense Ratio, Exit Load, Riskometer are injected via React after load
  - Simple httpx/BeautifulSoup will return skeleton HTML with empty data fields

Strategy per source type:
  - source == "groww"      → Playwright (wait for selector '.data1Fundv2' or similar)
  - source == "groww_help" → Playwright
  - source == "amc"        → httpx (Mirae Asset site is mostly static)
  - source == "amfi"       → httpx
  - source == "sebi"       → httpx
  - source == "cams"       → httpx

Rate limiting: 1 req/sec per domain, random jitter 0.5–1.5s
Retry:         Exponential backoff, max 3 retries on 5xx / timeout
robots.txt:    Checked before adding any domain to sources.json
"""

import asyncio
import random
import time
from pathlib import Path
from typing import Optional
import httpx
from playwright.async_api import async_playwright, Browser, Page
from urllib.robotparser import RobotFileParser

# Domains that require JS rendering
JS_RENDERED_DOMAINS = {"groww.in", "www.groww.in"}

# Playwright wait strategy for Groww fund pages
GROWW_FUND_WAIT_SELECTOR = "div[class*='fnd0MobileNameText'], div[class*='expenseRatio'], .fundDetailCard"
GROWW_WAIT_TIMEOUT_MS = 10_000  # 10 seconds

# HTTP timeouts for static pages
HTTP_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# TODO: Implement scraper (Playwright branch + httpx branch)
# ---------------------------------------------------------------------------

class Scraper:
    """
    Unified async scraper.
    Uses Playwright for JS-rendered pages (Groww), httpx for static pages.
    """

    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self._domain_last_request: dict[str, float] = {}
        self._browser: Optional[Browser] = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, *args):
        if self._browser:
            await self._browser.close()
        await self._playwright.stop()

    async def fetch(self, url: str, source_type: str = "static") -> Optional[str]:
        """
        Fetch page content as a string.

        Args:
            url:         Target URL
            source_type: One of 'groww', 'groww_help', 'amc', 'amfi', 'sebi', 'cams'

        Returns:
            Page HTML string or None on failure.
        """
        domain = self._domain(url)
        await self._throttle(domain)

        if source_type in ("groww", "groww_help"):
            return await self._fetch_playwright(url)
        else:
            return await self._fetch_httpx(url)

    async def _fetch_playwright(self, url: str) -> Optional[str]:
        """Use Playwright headless browser to render JS-heavy pages."""
        raise NotImplementedError

    async def _fetch_httpx(self, url: str) -> Optional[str]:
        """Use httpx for lightweight static page fetching with retry."""
        raise NotImplementedError

    def _domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc

    async def _throttle(self, domain: str) -> None:
        """Enforce per-domain rate limiting with random jitter (0.5–1.5s)."""
        now = time.monotonic()
        last = self._domain_last_request.get(domain, 0)
        wait_time = self.rate_limit + random.uniform(0.5, 1.5)
        if (elapsed := now - last) < wait_time:
            await asyncio.sleep(wait_time - elapsed)
        self._domain_last_request[domain] = time.monotonic()

    def _is_allowed(self, url: str) -> bool:
        """Check robots.txt compliance. Returns True if scraping is allowed."""
        raise NotImplementedError
