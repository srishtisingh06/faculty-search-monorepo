"""
Scrapy spider: discovers department pages and faculty profiles
from static (non-JS) institute websites.

Run:
  scrapy crawl faculty_spider -s INSTITUTE_URL=https://www.iitb.ac.in \
      -s INSTITUTE_NAME="IIT Bombay" -s INSTITUTE_TYPE=IIT
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy import signals
from scrapy.http import Response

from configs.settings import RAW_DIR, TARGET_DEPARTMENTS


# Department keyword patterns (case-insensitive)
DEPT_PATTERNS = [re.compile(r"\b" + re.escape(d) + r"\b", re.I) for d in TARGET_DEPARTMENTS]

# Patterns that suggest a faculty listing page
FACULTY_PAGE_PATTERNS = [
    re.compile(r"\b(faculty|people|members|team|staff|professors|academics)\b", re.I)
]

# Patterns that suggest a single profile page
PROFILE_PATTERNS = [
    re.compile(r"/(faculty|people|profile|person|member|user)/[^/]+/?$", re.I),
    re.compile(r"\bprofile\b", re.I),
    re.compile(r"[?&]id=\d+", re.I),
]


def _is_dept_link(text: str, href: str) -> bool:
    combined = (text + " " + href).lower()
    return any(p.search(combined) for p in DEPT_PATTERNS)


def _is_faculty_listing(text: str, href: str) -> bool:
    combined = (text + " " + href).lower()
    return any(p.search(combined) for p in FACULTY_PAGE_PATTERNS)


def _is_profile_url(href: str) -> bool:
    return any(p.search(href) for p in PROFILE_PATTERNS)


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


class FacultySpider(scrapy.Spider):
    name = "faculty_spider"
    custom_settings = {
        "DEPTH_LIMIT": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "DOWNLOAD_DELAY": 1.5,
        "RETRY_TIMES": 3,
        "HTTPCACHE_ENABLED": True,
        "ROBOTSTXT_OBEY": True,
    }

    def __init__(self, institute_url: str, institute_name: str, institute_type: str, **kwargs):
        super().__init__(**kwargs)
        self.institute_url = institute_url.rstrip("/")
        self.institute_name = institute_name
        self.institute_type = institute_type
        self.allowed_domains = [urlparse(institute_url).netloc]
        self.start_urls = [institute_url]
        self._seen: set[str] = set()

        RAW_DIR.mkdir(parents=True, exist_ok=True)

    # ── Entry point ───────────────────────────────────────────────────────────
    def parse(self, response: Response):
        """Parse home page: find department links."""
        yield from self._follow_dept_links(response)

    def parse_department(self, response: Response):
        """On a department page: find faculty listing links."""
        yield from self._follow_faculty_listing_links(response)
        yield from self._follow_profile_links(response)

    def parse_faculty_listing(self, response: Response):
        """On a faculty listing page: collect profile links + handle pagination."""
        yield from self._follow_profile_links(response)
        yield from self._follow_pagination(response)

    def parse_profile(self, response: Response):
        """Save raw HTML of a faculty profile page."""
        dept = response.meta.get("department", "")
        raw_path = RAW_DIR / self.institute_type / self.institute_name.replace(" ", "_")
        raw_path.mkdir(parents=True, exist_ok=True)
        fname = raw_path / f"{_url_hash(response.url)}.html"
        fname.write_bytes(response.body)

        yield {
            "source": "scrapy",
            "institute_name": self.institute_name,
            "institute_type": self.institute_type,
            "department_guess": dept,
            "profile_url": response.url,
            "raw_html_path": str(fname),
        }

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _follow_dept_links(self, response: Response):
        for a in response.css("a[href]"):
            href = a.attrib["href"]
            text = a.css("::text").get("") or ""
            abs_url = urljoin(response.url, href)
            if not self._should_follow(abs_url):
                continue
            if _is_dept_link(text, abs_url):
                dept_name = self._match_dept(text + " " + abs_url)
                yield response.follow(
                    abs_url,
                    callback=self.parse_department,
                    meta={"department": dept_name},
                    errback=self._errback,
                )

    def _follow_faculty_listing_links(self, response: Response):
        dept = response.meta.get("department", "")
        for a in response.css("a[href]"):
            href = a.attrib["href"]
            text = a.css("::text").get("") or ""
            abs_url = urljoin(response.url, href)
            if not self._should_follow(abs_url):
                continue
            if _is_faculty_listing(text, abs_url):
                yield response.follow(
                    abs_url,
                    callback=self.parse_faculty_listing,
                    meta={"department": dept},
                    errback=self._errback,
                )

    def _follow_profile_links(self, response: Response):
        dept = response.meta.get("department", "")
        for a in response.css("a[href]"):
            href = a.attrib.get("href", "")
            abs_url = urljoin(response.url, href)
            if not self._should_follow(abs_url):
                continue
            if _is_profile_url(abs_url):
                yield response.follow(
                    abs_url,
                    callback=self.parse_profile,
                    meta={"department": dept},
                    errback=self._errback,
                )

    def _follow_pagination(self, response: Response):
        """Follow next-page links on faculty listing pages."""
        dept = response.meta.get("department", "")
        for sel in response.css('a[href*="page"], a[href*="offset"], a.next, a[rel="next"]'):
            href = sel.attrib.get("href", "")
            abs_url = urljoin(response.url, href)
            if self._should_follow(abs_url):
                yield response.follow(
                    abs_url,
                    callback=self.parse_faculty_listing,
                    meta={"department": dept},
                    errback=self._errback,
                )

    def _should_follow(self, url: str) -> bool:
        if url in self._seen:
            return False
        parsed = urlparse(url)
        if parsed.netloc and parsed.netloc not in self.allowed_domains:
            return False
        if not parsed.scheme.startswith("http"):
            return False
        self._seen.add(url)
        return True

    def _match_dept(self, text: str) -> str:
        from configs.settings import DEPARTMENT_CANONICAL
        text_lower = text.lower()
        for key, canonical in DEPARTMENT_CANONICAL.items():
            if key.lower() in text_lower:
                return canonical
        return ""

    def _errback(self, failure):
        self.logger.error("Request failed: %s | %s", failure.request.url, repr(failure))
