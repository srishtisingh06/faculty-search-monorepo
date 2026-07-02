"""
extract_bootstrap.py

Reusable Bootstrap-card faculty extractor.

Works for pages like IIT Hyderabad MAE where each faculty is inside:
<div class="card">
  img.card-img
  h4.card-title / .fac-head -> name
  h5.fac-des-head -> designation
  p with "Areas of Research" -> research interests
  right-side p tags -> office/email/phone
  a button -> homepage/profile URL
</div>

Change CONFIG values below, then run:
python extract_bootstrap.py
"""

import re
from urllib.parse import urljoin
import argparse
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile


# ==========================
# CHANGE ONLY THESE VALUES
# ==========================

parser = argparse.ArgumentParser()

parser.add_argument("--html", required=True)
parser.add_argument("--institute", required=True)
parser.add_argument("--url", required=True)
parser.add_argument("--department", required=True)
parser.add_argument("--city", default="")
parser.add_argument("--state", default="")
parser.add_argument("--type", default="IIT")

args = parser.parse_args()

HTML_FILE = args.html
INSTITUTE_NAME = args.institute
INSTITUTE_URL = args.url
DEPARTMENT = args.department
LISTING_URL = args.url
CITY = args.city
STATE = args.state
INSTITUTE_TYPE = args.type
DEDUP_BY_NAME = True

# ==========================


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_url(url: str) -> str:
    url = clean_text(url)
    if not url:
        return ""
    return urljoin(LISTING_URL, url)


def normalize_email(text: str) -> str:
    text = clean_text(text)
    text = text.replace("[at]", "@")
    text = text.replace(" [at] ", "@")
    text = text.replace(" at ", "@")
    text = text.replace(" dot ", ".")
    text = text.replace(" @ ", "@")
    text = text.replace(" @", "@")
    text = text.replace("@ ", "@")
    return text

def main():
    ...

if __name__ == "__main__":
    main()
def is_email(text: str) -> bool:
    t = normalize_email(text).lower()
    return "@" in t and "." in t


def is_phone(text: str) -> bool:
    t = clean_text(text)
    digits = re.sub(r"\D", "", t)
    return len(digits) >= 7 and ("+" in t or "-" in t or "(" in t or ")" in t or len(digits) >= 10)


def split_interests(text: str):
    text = clean_text(text)
    text = re.sub(r"Areas?\s+of\s+Research\s*:?", "", text, flags=re.I)
    text = re.sub(r"Research\s+Areas?\s*:?", "", text, flags=re.I)
    text = clean_text(text)

    if not text:
        return []

    parts = re.split(r",|;|\|", text)
    return [clean_text(p) for p in parts if clean_text(p)][:10]


def extract_research(card):
    # First try paragraph containing "Areas of Research"
    for p in card.find_all(["p", "div"]):
        txt = clean_text(p.get_text(" ", strip=True))
        if re.search(r"Areas?\s+of\s+Research", txt, re.I):
            return txt

    # Fallback: class pfont1 often stores area text
    for p in card.select(".pfont1"):
        txt = clean_text(p.get_text(" ", strip=True))
        if len(txt) > 20 and not is_email(txt) and not is_phone(txt):
            if "PhD" not in txt:
                return txt

    return ""


def extract_contact(card):
    office = ""
    email = ""
    phone = ""

    # right-side badge usually stores office, email, phone
    contact_blocks = card.select(".fac-set .card-text, .badge .card-text")

    values = [clean_text(x.get_text(" ", strip=True)) for x in contact_blocks]
    values = [v for v in values if v]

    for val in values:
        norm_email = normalize_email(val)

        if not email and is_email(norm_email):
            email = norm_email
        elif not phone and is_phone(val):
            phone = val
        elif not office:
            office = val

    return office, email, phone


def extract_publications(card):
    pubs = []

    for heading in card.find_all(["h3", "h4", "h5"]):
        htxt = clean_text(heading.get_text(" ", strip=True)).lower()

        if "publication" in htxt:
            ul = heading.find_next("ul")
            if ul:
                for li in ul.find_all("li")[:5]:
                    txt = clean_text(li.get_text(" ", strip=True))
                    if txt:
                        pubs.append(txt)

    return pubs[:5]


def extract_faculty(html: str):
    soup = BeautifulSoup(html, "lxml")

    cards = soup.find_all("div", class_=lambda c: c and "card" in c.split())

    records = []
    seen = set()

    for card in cards:
        name_tag = (
            card.select_one(".fac-head")
            or card.select_one(".card-title")
            or card.find(["h3", "h4", "h5"])
        )

        name = clean_text(name_tag.get_text(" ", strip=True)) if name_tag else ""

        if not name:
            continue

        # Avoid fake card titles
        bad_names = {"publications", "patents", "book chapters", "read more"}
        if name.lower() in bad_names:
            continue

        if DEDUP_BY_NAME:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)

        desig_tag = card.select_one(".fac-des-head")
        designation = clean_text(desig_tag.get_text(" ", strip=True)) if desig_tag else "Faculty"

        phd = ""
        phd_tag = name_tag.find_next("p") if name_tag else None
        if phd_tag:
            phd_text = clean_text(phd_tag.get_text(" ", strip=True))
            if "phd" in phd_text.lower():
                phd = phd_text

        research_text = extract_research(card)
        office, email, phone = extract_contact(card)

        img = card.select_one("img")
        image_url = normalize_url(img.get("src", "")) if img else ""

        profile_url = ""

        # Prefer homepage / personal page buttons
        for a in card.find_all("a", href=True):
            href = a.get("href", "")
            txt = clean_text(a.get_text(" ", strip=True)).lower()

            if any(x in txt for x in ["home page", "homepage", "profile", "read more"]):
                profile_url = normalize_url(href)
                break

        if not profile_url:
            for a in card.find_all("a", href=True):
                href = a.get("href", "")
                if href and not href.startswith("#"):
                    profile_url = normalize_url(href)
                    break

        if not profile_url:
            profile_url = f"{LISTING_URL}#{slugify(name)}"

        records.append({
            "name": name,
            "designation": designation,
            "qualification": phd,
            "office": office,
            "email": email,
            "phone": phone,
            "research_areas": split_interests(research_text),
            "profile_url": profile_url,
            "profile_image": image_url,
            "publications": extract_publications(card),
        })

    return records


def save_records(records):
    saved = 0
    seen_urls = set()

    for r in records:
        profile_url = r["profile_url"]

        if profile_url in seen_urls:
            profile_url = f"{profile_url}-{slugify(r['name'])}"

        seen_urls.add(profile_url)

        profile = {
            "faculty_name": r["name"],
            "designation": r.get("designation") or "Faculty",
            "email": r.get("email", ""),
            "phone": r.get("phone", ""),
            "office": r.get("office", ""),
            "research_interests": r.get("research_areas", []),
            "profile_url": profile_url,
            "profile_image": r.get("profile_image", ""),
            "education": [r.get("qualification", "")] if r.get("qualification") else [],
            "publications": r.get("publications", []),
            "institute_name": INSTITUTE_NAME,
            "institute_type": INSTITUTE_TYPE,
            "department": DEPARTMENT,
        }

        ok = save_faculty_profile(
            profile,
            institute_url=INSTITUTE_URL,
            institute_type=INSTITUTE_TYPE,
            city=CITY,
            state=STATE,
        )

        if ok:
            saved += 1

    return saved


def main():
    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()

    records = extract_faculty(html)

    print(f"Extracted: {len(records)} faculty")

    for r in records[:10]:
        print(
            f"{r['name']} | {r['designation']} | "
            f"{r['email']} | {', '.join(r['research_areas'][:3])}"
        )

    saved = save_records(records)

    print(f"Saved {saved}/{len(records)} faculty to PostgreSQL")


if __name__ == "__main__":
    main()
