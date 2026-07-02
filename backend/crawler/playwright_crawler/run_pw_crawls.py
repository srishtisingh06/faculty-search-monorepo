"""
Playwright batch runner — crawls all institutes where Scrapy got 0 results.

Usage:
    python -m crawler.playwright_crawler.run_pw_crawls
    python -m crawler.playwright_crawler.run_pw_crawls --all   # force all institutes
"""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from configs.settings import EXCEL_FILES, LOG_DIR, PROCESSED_DIR
from crawler.playwright_crawler.pw_crawler import crawl_institute
from data.seed_reader import load_all_institutes

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "pw_crawl_runner.log"),
    ],
)
logger = logging.getLogger(__name__)

CHECKPOINT_FILE = Path("logs/pw_checkpoint.json")
SCRAPY_JSONL = Path("data/raw/scraped_faculty_spider.jsonl")


def _institutes_with_scrapy_results() -> set[str]:
    """Return set of institute names that Scrapy already got results for."""
    if not SCRAPY_JSONL.exists():
        return set()
    names: set[str] = set()
    with SCRAPY_JSONL.open() as f:
        for line in f:
            try:
                meta = json.loads(line.strip())
                name = meta.get("institute_name", "")
                if name:
                    names.add(name)
            except json.JSONDecodeError:
                pass
    return names


def _load_checkpoint() -> set[str]:
    if CHECKPOINT_FILE.exists():
        return set(json.loads(CHECKPOINT_FILE.read_text()))
    return set()


def _save_checkpoint(done: set[str]):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(sorted(done), indent=2))


async def run_all(force_all: bool = False):
    institutes = load_all_institutes(
        EXCEL_FILES["iit"], EXCEL_FILES["nit_bits"], EXCEL_FILES["bits"]
    )
    done = _load_checkpoint()
    scrapy_done = _institutes_with_scrapy_results()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    total = len(institutes)
    skipped_scrapy = 0

    for i, inst in enumerate(institutes, 1):
        name = inst["name"]

        if name in done:
            logger.info("[%d/%d] Skip (PW done): %s", i, total, name)
            continue

        if not force_all and name in scrapy_done:
            logger.info("[%d/%d] Skip (Scrapy has data): %s", i, total, name)
            skipped_scrapy += 1
            continue

        logger.info("[%d/%d] Playwright crawl: %s", i, total, name)
        try:
            results = await crawl_institute(inst["url"], name, inst["type"])
            out = PROCESSED_DIR / f"{name.replace(' ', '_')}_pw.jsonl"
            with out.open("w") as f:
                for r in results:
                    f.write(json.dumps(r) + "\n")
            logger.info("  → %d profiles saved", len(results))
            done.add(name)
            _save_checkpoint(done)
        except Exception as exc:
            logger.error("Playwright failed for %s: %s", name, exc)

    logger.info(
        "PW batch done. Crawled: %d, Skipped (scrapy): %d, Total: %d",
        len(done), skipped_scrapy, total,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true",
                        help="Crawl all institutes even if Scrapy already got results")
    args = parser.parse_args()
    asyncio.run(run_all(force_all=args.all))


if __name__ == "__main__":
    main()
