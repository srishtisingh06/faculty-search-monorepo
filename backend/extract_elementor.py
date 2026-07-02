""""
extract_elementor.py

Reusable Elementor/WordPress faculty extractor.

Best for pages like IIT Hyderabad AI where each faculty card is built with
Elementor containers and contains:
- h4 faculty name
- text block with designation / office
- "Research Interests:" heading followed by text
- optional "Know More" profile link
- optional image

How to use:
1. Change CONFIG values below.
2. Run: python extract_elementor.py
"""
import argparse
import re
from urllib.parse import urljoin

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
def main():
    ...

if __name__ == "__main__":
    main()

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def split_interests(text: str):
    text = clean_text(text)
    if not text:
        return []

    text = text.replace("Research Interests:", "")
    text = text.replace("Research Interest:", "")
    text = clean_text(text)

    parts = re.split(r",|;|\|", text)
    interests = [clean_text(p) for p in parts if clean_text(p)]

    return interests[:8]


def looks_like_faculty_leaf(container) -> bool:
    h4s = container.find_all("h4")
    if len(h4s) != 1:
        return False

    nested = container.find("div", attrs={"data_element_type": "container"})
    if nested is not None:
        return False

    # BeautifulSoup keeps hyphenated attrs as exact keys
    nested = container.find("div", attrs={"data-element_type": "container"})
    if nested is not None:
        return False

    text = clean_text(container.get_text(" ", strip=True))
    if len(text) < 5:
        return False

    return True


def extract_research(container) -> str:
    for h in container.find_all(["h5", "h4", "h3"]):
        label = clean_text(h.get_text(" ", strip=True)).lower()

        if "research" in label and "interest" in label:
            parent_widget = h.find_parent("div", attrs={"data-widget_type": "heading.default"})

            if parent_widget:
                nxt = parent_widget.find_next_sibling()
                hops = 0

                while nxt and hops < 5:
                    txt = clean_text(nxt.get_text(" ", strip=True))

                    if txt and "research interest" not in txt.lower():
                        return txt

                    nxt = nxt.find_next_sibling()
                    hops += 1

            p = h.find_next("p")
            if p:
                return clean_text(p.get_text(" ", strip=True))

    text = clean_text(container.get_text(" ", strip=True))
    match = re.search(r"Research Interests?:\s*(.*?)(?:Know More|$)", text, re.I)

    if match:
        return clean_text(match.group(1))

    return ""


def extract_designation_and_office(container, name: str, research_text: str) -> tuple[str, str]:
    text = clean_text(container.get_text(" ", strip=True))
    text = re.sub(r"^" + re.escape(name) + r"\s*", "", text)

    if "Research Interests:" in text:
        before_research = text.split("Research Interests:", 1)[0]
    elif "Research Interest:" in text:
        before_research = text.split("Research Interest:", 1)[0]
    else:
        before_research = text

    before_research = clean_text(before_research.replace("Know More", ""))

    designation = ""
    office = ""

    known_designations = [
        "Distinguished Professor",
        "Head of the Department",
        "Professor",
        "Associate Professor",
        "Assistant Professor",
        "Adjunct Faculty",
        "Faculty",
    ]

    for d in known_designations:
        if d.lower() in before_research.lower():
            designation = d
            office = clean_text(re.sub(re.escape(d), "", before_research, flags=re.I).strip(" ,;-"))
            break

    if not designation:
        designation = "Faculty"
        office = before_research

    return designation, office


def normalize_url(url: str) -> str:
    url = clean_text(url)
    if not url:
        return ""
    return urljoin(LISTING_URL, url)


def extract_faculty(html: str):
    soup = BeautifulSoup(html, "lxml")

    containers = soup.find_all("div", attrs={"data-element_type": "container"})

    records = []
    seen = set()

    for container in containers:
        if not looks_like_faculty_leaf(container):
            continue

        h4 = container.find("h4")
        name = clean_text(h4.get_text(" ", strip=True)) if h4 else ""

        if not name:
            continue

        if DEDUP_BY_NAME:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)

        research_text = extract_research(container)
        designation, office = extract_designation_and_office(container, name, research_text)

        profile_url = ""
        a = container.find("a", href=True)

        if a:
            href = a.get("href", "")
            if href and "#" not in href:
                profile_url = normalize_url(href)

        if not profile_url:
            profile_url = f"{LISTING_URL}#{slugify(name)}"

        image_url = ""
        img = container.find_previous("img")

        if img:
            image_url = normalize_url(img.get("src", ""))

        records.append({
            "name": name,
            "designation": designation,
            "office": office,
            "email": "",
            "phone": "",
            "research_areas": split_interests(research_text),
            "profile_url": profile_url,
            "profile_image": image_url,
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
            f"{', '.join(r['research_areas'][:3])}"
        )

    saved = save_records(records)

    print(f"Saved {saved}/{len(records)} faculty to PostgreSQL")


if __name__ == "__main__":
    main()
