"""
scraper.py
----------
Async scraper supporting two fetch modes:

  Static pages (AMC, AMFI, SEBI, CAMS):
    → Uses `requests` + `BeautifulSoup` (simple, no JS needed)

  JavaScript-rendered pages (Groww fund detail / help pages):
    → Uses `playwright` headless Chromium to wait for React hydration

Rate limiting : 1–2 sec random jitter between requests (per domain)
Retry         : exponential backoff, max 3 retries on 5xx / timeout
robots.txt    : compliance checked before first request to each domain
"""

import asyncio
import hashlib
import random
import time
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from playwright.async_api import async_playwright, Browser

logger = logging.getLogger(__name__)

# Domains that serve data via JavaScript and need Playwright
JS_RENDERED_DOMAINS = {"groww.in", "www.groww.in"}

# Playwright: selector to wait for before extracting HTML on Groww pages
GROWW_WAIT_SELECTOR = "main, article, .fundDetailCard, .kycContainer"
GROWW_WAIT_TIMEOUT_MS = 15_000  # 15 seconds max

HTTP_TIMEOUT = 20          # seconds
MAX_RETRIES  = 3
RATE_LIMIT   = 1.0         # minimum seconds between requests to the same domain
JITTER       = (0.5, 1.5)  # extra random wait added to RATE_LIMIT

# Cache of robots.txt per domain  (domain → RobotFileParser)
_robots_cache: dict[str, RobotFileParser] = {}


class Scraper:
    """
    Async context-manager scraper.

    Usage:
        async with Scraper() as s:
            html = await s.fetch(url, source_type="amc")
    """

    def __init__(self):
        self._domain_last_req: dict[str, float] = {}
        self._browser: Optional[Browser] = None
        self._playwright = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        logger.info("Playwright browser started")
        return self

    async def __aexit__(self, *_):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Playwright browser closed")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch(self, url: str, source_type: str = "static") -> Optional[str]:
        """
        Fetch a page and return its raw HTML (or None on failure).

        Args:
            url:         Target URL.
            source_type: One of 'groww', 'groww_help', 'amc', 'amfi', 'sebi', 'cams'.

        Returns:
            Raw HTML string, or None if the page could not be fetched.
        """
        domain = _domain(url)

        if not self._is_allowed(url):
            logger.warning("robots.txt disallows scraping: %s", url)
            return None

        await self._throttle(domain)

        if source_type in ("groww", "groww_help"):
            return await self._fetch_playwright(url)
        return await self._fetch_httpx(url)

    # ------------------------------------------------------------------
    # Internal fetch methods
    # ------------------------------------------------------------------

    async def _fetch_playwright(self, url: str) -> Optional[str]:
        """Headless Chromium fetch for JS-rendered pages (Groww)."""
        if not self._browser:
            raise RuntimeError("Scraper must be used as an async context manager")
        page = await self._browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=GROWW_WAIT_TIMEOUT_MS)
            # Try waiting for a meaningful element; ignore timeout gracefully
            try:
                await page.wait_for_selector(GROWW_WAIT_SELECTOR, timeout=GROWW_WAIT_TIMEOUT_MS)
            except Exception:
                logger.warning("Selector not found within timeout on %s — using whatever rendered", url)
            html = await page.content()
            logger.info("Playwright fetched: %s (%d bytes)", url, len(html))
            return html
        except Exception as exc:
            logger.error("Playwright error on %s: %s", url, exc)
            return None
        finally:
            await page.close()

    async def _fetch_httpx(self, url: str) -> Optional[str]:
        """Lightweight async HTTP fetch with retry for static pages."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; MFBot/1.0; "
                "+https://github.com/your-org/mf-faq-chatbot)"
            )
        }
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=HTTP_TIMEOUT,
                    follow_redirects=True,
                    headers=headers,
                ) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        logger.info("httpx fetched: %s (%d bytes)", url, len(resp.text))
                        return resp.text
                    elif resp.status_code in (429, 500, 502, 503, 504):
                        wait = 2 ** attempt
                        logger.warning(
                            "HTTP %d on %s — retry %d/%d in %ds",
                            resp.status_code, url, attempt, MAX_RETRIES, wait,
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.warning("HTTP %d on %s — skipping", resp.status_code, url)
                        return None
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                wait = 2 ** attempt
                logger.warning("Request error on %s (%s) — retry %d/%d in %ds", url, exc, attempt, MAX_RETRIES, wait)
                await asyncio.sleep(wait)
        logger.error("All %d retries failed for %s", MAX_RETRIES, url)
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _throttle(self, domain: str) -> None:
        """Enforce per-domain rate limiting with random jitter."""
        now = time.monotonic()
        last = self._domain_last_req.get(domain, 0)
        wait = RATE_LIMIT + random.uniform(*JITTER)
        elapsed = now - last
        if elapsed < wait:
            await asyncio.sleep(wait - elapsed)
        self._domain_last_req[domain] = time.monotonic()

    def _is_allowed(self, url: str) -> bool:
        """
        Check robots.txt for the given URL.
        Returns True (allowed) if robots.txt is unreachable or doesn't restrict us.
        """
        domain = _domain(url)
        if domain not in _robots_cache:
            rp = RobotFileParser()
            robots_url = f"https://{domain}/robots.txt"
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception:
                # If robots.txt is unreachable, assume allowed
                pass
            _robots_cache[domain] = rp
        return _robots_cache[domain].can_fetch("*", url)


# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------

def _domain(url: str) -> str:
    """Extract netloc (domain) from a URL."""
    return urlparse(url).netloc


def url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug."""
    parsed = urlparse(url)
    path_slug = parsed.path.strip("/").replace("/", "_").replace("-", "_")
    # Use a short hash suffix to guarantee uniqueness
    short_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    base = f"{parsed.netloc.replace('.', '_')}__{path_slug}"[:80]
    return f"{base}__{short_hash}"
