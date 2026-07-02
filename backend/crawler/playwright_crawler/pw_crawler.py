"""
Playwright-based crawler for JavaScript-rendered faculty pages.
Handles: SPA routing, lazy-loaded lists, AJAX pagination, infinite scroll.

Usage:
    python -m crawler.playwright_crawler.pw_crawler \
        --url https://www.iitb.ac.in/en/education/faculty \
        --institute "IIT Bombay" --type IIT
"""
import asyncio
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page, async_playwright

from configs.settings import PLAYWRIGHT_HEADLESS, PLAYWRIGHT_TIMEOUT, RAW_DIR, TARGET_DEPARTMENTS

logger = logging.getLogger(__name__)

DEPT_RE = re.compile(
    r"\b(" + "|".join(re.escape(d) for d in TARGET_DEPARTMENTS) + r")\b", re.I
)
FACULTY_PAGE_RE = re.compile(r"\b(faculty|people|members|team|staff|professors|academics)\b", re.I)
PROFILE_RE = re.compile(r"/(faculty|people|profile|person|member)/[^/]+/?$", re.I)


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


async def _wait_for_content(page: Page, selector: str = "body", timeout: int = 10_000):
    """Wait for a meaningful content selector to appear."""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
    except Exception:
        pass
    await page.wait_for_load_state("networkidle", timeout=timeout)


async def _scroll_to_bottom(page: Page, max_scrolls: int = 20):
    """Handle infinite-scroll pages."""
    prev_height = 0
    for _ in range(max_scrolls):
        curr_height: int = await page.evaluate("document.body.scrollHeight")
        if curr_height == prev_height:
            break
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        prev_height = curr_height


async def _get_all_links(page: Page, base_url: str) -> list[dict]:
    """Extract all anchor hrefs and their visible text from the page."""
    raw = await page.evaluate("""
        Array.from(document.querySelectorAll('a[href]')).map(a => ({
            href: a.href,
            text: (a.innerText || a.textContent || '').trim().slice(0, 120)
        }))
    """)
    domain = urlparse(base_url).netloc
    result = []
    for item in raw:
        href = item.get("href", "")
        parsed = urlparse(href)
        if parsed.netloc and parsed.netloc != domain:
            continue
        if not href.startswith("http"):
            continue
        result.append({"href": href, "text": item.get("text", "")})
    return result


async def crawl_institute(
    institute_url: str,
    institute_name: str,
    institute_type: str,
    max_profiles: int = 500,
) -> list[dict]:
    """
    Main entry: visits an institute homepage, finds dept pages,
    finds faculty listing pages, extracts profile pages.
    Returns list of raw profile dicts.
    """
    results = []
    visited: set[str] = set()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (compatible; AcademiaBot/1.0; "
                "+https://github.com/yourorg/faculty-search)"
            ),
            java_script_enabled=True,
        )
        context.set_default_timeout(PLAYWRIGHT_TIMEOUT)

        # Step 1: Home page → find department links
        page = await context.new_page()
        logger.info("Opening: %s", institute_url)
        try:
            await page.goto(institute_url)
            await _wait_for_content(page)
        except Exception as exc:
            logger.error("Failed to open %s: %s", institute_url, exc)
            await browser.close()
            return results

        links = await _get_all_links(page, institute_url)
        dept_urls = [
            lk["href"] for lk in links
            if DEPT_RE.search(lk["text"] + " " + lk["href"])
            and lk["href"] not in visited
        ]
        logger.info("Found %d dept links at %s", len(dept_urls), institute_url)

        # Step 2: Dept pages → faculty listing links
        listing_urls: list[tuple[str, str]] = []  # (url, dept_name)
        for dept_url in dept_urls[:10]:  # cap per institute
            if dept_url in visited:
                continue
            visited.add(dept_url)
            dept_name = _match_dept(dept_url)
            try:
                await page.goto(dept_url)
                await _wait_for_content(page)
                dept_links = await _get_all_links(page, institute_url)
                for lk in dept_links:
                    if (
                        FACULTY_PAGE_RE.search(lk["text"] + " " + lk["href"])
                        and lk["href"] not in visited
                    ):
                        listing_urls.append((lk["href"], dept_name))
            except Exception as exc:
                logger.warning("Dept page error %s: %s", dept_url, exc)

        # Also check the home page itself for faculty links
        for lk in links:
            if FACULTY_PAGE_RE.search(lk["text"] + " " + lk["href"]) and lk["href"] not in visited:
                listing_urls.append((lk["href"], ""))

        logger.info("Found %d faculty listing pages", len(listing_urls))

        # Step 3: Faculty listing pages → profile pages
        profile_urls: list[tuple[str, str]] = []
        for listing_url, dept_name in listing_urls[:15]:
            if listing_url in visited:
                continue
            visited.add(listing_url)
            try:
                await page.goto(listing_url)
                await _wait_for_content(page)
                await _scroll_to_bottom(page)  # handle infinite scroll

                # Click "Load more" buttons if present
                for _ in range(5):
                    btn = page.locator(
                        'button:has-text("Load more"), button:has-text("Show all"), '
                        'a:has-text("Next"), [aria-label="next page"]'
                    )
                    if await btn.count() > 0:
                        await btn.first.click()
                        await asyncio.sleep(1.5)
                        await _wait_for_content(page)
                    else:
                        break

                page_links = await _get_all_links(page, institute_url)
                for lk in page_links:
                    if PROFILE_RE.search(lk["href"]) and lk["href"] not in visited:
                        profile_urls.append((lk["href"], dept_name))

            except Exception as exc:
                logger.warning("Listing page error %s: %s", listing_url, exc)

        logger.info("Found %d profile URLs", len(profile_urls))

        # Step 4: Scrape each profile page
        out_dir = RAW_DIR / institute_type / institute_name.replace(" ", "_")
        out_dir.mkdir(parents=True, exist_ok=True)

        for prof_url, dept_name in profile_urls[:max_profiles]:
            if prof_url in visited:
                continue
            visited.add(prof_url)
            try:
                await page.goto(prof_url)
                await _wait_for_content(page)
                html = await page.content()
                fname = out_dir / f"{_url_hash(prof_url)}.html"
                fname.write_text(html, encoding="utf-8")
                results.append({
                    "source": "playwright",
                    "institute_name": institute_name,
                    "institute_type": institute_type,
                    "department_guess": dept_name,
                    "profile_url": prof_url,
                    "raw_html_path": str(fname),
                })
            except Exception as exc:
                logger.warning("Profile error %s: %s", prof_url, exc)

        await browser.close()

    logger.info("Crawl done for %s: %d profiles saved", institute_name, len(results))
    return results


def _match_dept(text: str) -> str:
    from configs.settings import DEPARTMENT_CANONICAL
    for key, canonical in DEPARTMENT_CANONICAL.items():
        if key.lower() in text.lower():
            return canonical
    return ""


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--institute", required=True)
    parser.add_argument("--type", dest="inst_type", default="IIT")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    results = await crawl_institute(args.url, args.institute, args.inst_type)
    out = Path("data/processed") / f"{args.institute.replace(' ', '_')}_profiles.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Saved {len(results)} profiles → {out}")


if __name__ == "__main__":
    asyncio.run(main())
