"""
Runs the Scrapy faculty spider for every institute in the seed files.
Skips institutes already processed (based on a checkpoint file).

Usage:
    python -m crawler.scrapy_spiders.run_all_crawls
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

from configs.settings import EXCEL_FILES, LOG_DIR
from data.seed_reader import load_all_institutes

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "crawl_runner.log"),
    ],
)
logger = logging.getLogger(__name__)

CHECKPOINT_FILE = Path("logs/scrapy_checkpoint.json")


def _load_checkpoint() -> set[str]:
    if CHECKPOINT_FILE.exists():
        return set(json.loads(CHECKPOINT_FILE.read_text()))
    return set()


def _save_checkpoint(done: set[str]) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(sorted(done), indent=2))


def run_spider(url: str, name: str, inst_type: str) -> bool:
    """Invoke scrapy crawl in a subprocess. Returns True on success."""
    cmd = [
        "scrapy", "crawl", "faculty_spider",
        "-s", f"INSTITUTE_URL={url}",
        "-s", f"INSTITUTE_NAME={name}",
        "-s", f"INSTITUTE_TYPE={inst_type}",
        "--logfile", str(LOG_DIR / f"scrapy_{name.replace(' ', '_')}.log"),
    ]
    try:
        result = subprocess.run(cmd, timeout=600, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning("Spider returned non-zero for %s: %s", name, result.stderr[:300])
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.error("Timed out crawling %s", name)
        return False
    except Exception as exc:
        logger.error("Error running spider for %s: %s", name, exc)
        return False


def main():
    institutes = load_all_institutes(
        EXCEL_FILES["iit"],
        EXCEL_FILES["nit_bits"],
        EXCEL_FILES["bits"],
    )
    done = _load_checkpoint()
    total = len(institutes)
    logger.info("Starting batch crawl: %d institutes (%d already done)", total, len(done))

    for i, inst in enumerate(institutes, 1):
        key = inst["url"]
        if key in done:
            logger.info("[%d/%d] Skipping (done): %s", i, total, inst["name"])
            continue
        logger.info("[%d/%d] Crawling: %s  (%s)", i, total, inst["name"], inst["url"])
        success = run_spider(inst["url"], inst["name"], inst["type"])
        if success:
            done.add(key)
            _save_checkpoint(done)
        else:
            logger.warning("Failed: %s — will retry next run", inst["name"])

    logger.info("Batch crawl complete. Done: %d / %d", len(done), total)


if __name__ == "__main__":
    main()
