"""
Reads institute seed data from Excel files.
Returns a unified list of {name, url, type} dicts for use by crawlers.
"""
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def _normalise_url(raw: str) -> str:
    """Ensure URL has https:// scheme."""
    if not raw or not isinstance(raw, str):
        return ""
    raw = raw.strip().rstrip("/")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


def _load_iit(path: Path) -> list[dict]:
    df = pd.read_excel(path, sheet_name="IIT Colleges")
    df.columns = df.columns.str.strip()
    records = []
    for _, row in df.iterrows():
        url = _normalise_url(str(row.get("Website", "")))
        if not url:
            continue
        records.append({
            "name": str(row["College Name"]).strip(),
            "url": url,
            "type": "IIT",
            "city": str(row.get("City", "")).strip(),
            "state": str(row.get("State", "")).strip(),
        })
    logger.info("Loaded %d IITs from %s", len(records), path.name)
    return records


def _load_nit_bits(path: Path) -> list[dict]:
    xl = pd.read_excel(path, sheet_name=None)
    records = []
    for sheet_name, df in xl.items():
        df.columns = df.columns.str.strip()
        inst_type = "NIT" if "NIT" in sheet_name.upper() else "BITS"
        for _, row in df.iterrows():
            url = _normalise_url(str(row.get("Website", "")))
            if not url:
                continue
            records.append({
                "name": str(row["College Name"]).strip(),
                "url": url,
                "type": inst_type,
                "city": str(row.get("City", "")).strip(),
                "state": str(row.get("State", "")).strip(),
            })
    logger.info("Loaded %d institutes from %s", len(records), path.name)
    return records


def _load_bits(path: Path) -> list[dict]:
    df = pd.read_excel(path, sheet_name="BITS Colleges")
    df.columns = df.columns.str.strip()
    records = []
    for _, row in df.iterrows():
        url = _normalise_url(str(row.get("Website", "")))
        if not url:
            continue
        name = str(row["College Name"]).strip()
        campus = str(row.get("Campus", "")).strip()
        records.append({
            "name": f"{name} – {campus}" if campus else name,
            "url": url,
            "type": "BITS",
            "city": str(row.get("City", "")).strip(),
            "state": str(row.get("State", "")).strip(),
        })
    logger.info("Loaded %d BITS campuses from %s", len(records), path.name)
    return records


def load_all_institutes(
    iit_path: Path,
    nit_bits_path: Path,
    bits_path: Path,
) -> list[dict]:
    """
    Returns deduplicated institute list from all seed files.
    Each entry: {name, url, type, city, state}
    """
    records: list[dict] = []
    records.extend(_load_iit(iit_path))
    records.extend(_load_nit_bits(nit_bits_path))
    records.extend(_load_bits(bits_path))

    # Deduplicate by URL
    seen: set[str] = set()
    unique = []
    for r in records:
        key = r["url"].lower().rstrip("/")
        if key not in seen:
            seen.add(key)
            unique.append(r)

    logger.info("Total unique institutes: %d", len(unique))
    return unique


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from configs.settings import EXCEL_FILES

    institutes = load_all_institutes(
        EXCEL_FILES["iit"],
        EXCEL_FILES["nit_bits"],
        EXCEL_FILES["bits"],
    )
    for inst in institutes[:5]:
        print(inst)
