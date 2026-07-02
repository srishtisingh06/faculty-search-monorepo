"""
extract_kingster.py

Reusable extractor for Kingster / GDLR faculty pages
(e.g. IIT Hyderabad Mathematics).

Change CONFIG values and run:
    python extract_kingster.py
"""
import argparse
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

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

def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()


def split_research(t):
    t = re.sub(r"Area[s]? of Interest:?", "", clean(t), flags=re.I)
    return [x.strip() for x in re.split(r",|;", t) if x.strip()]


def save(records):
    c = 0
    for r in records:
        ok = save_faculty_profile(
            {
                "faculty_name": r["name"],
                "designation": r["designation"],
                "email": r["email"],
                "phone": r["phone"],
                "office": r["office"],
                "research_interests": r["research"],
                "profile_url": r["profile"],
                "profile_image": r["image"],
                "institute_name": INSTITUTE_NAME,
                "department": DEPARTMENT,
            },
            institute_url=INSTITUTE_URL,
            institute_type=INSTITUTE_TYPE,
            city=CITY,
            state=STATE,
        )
        if ok:
            c += 1
    return c


with open(HTML_FILE, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

cards = soup.select("div.gdlr-core-personnel-list")

records = []
seen = set()

for card in cards:
    name_tag = card.select_one(".gdlr-core-personnel-list-title")
    if not name_tag:
        continue

    name = clean(name_tag.get_text())
    if name.lower() in seen:
        continue
    seen.add(name.lower())

    profile = ""
    a = name_tag.find("a", href=True)
    if a:
        profile = urljoin(LISTING_URL, a["href"])

    img = ""
    im = card.select_one("img")
    if im:
        img = urljoin(LISTING_URL, im.get("src", ""))

    des = clean(card.select_one(".gdlr-core-personnel-list-position").get_text()) \
        if card.select_one(".gdlr-core-personnel-list-position") else "Faculty"

    office = ""
    email = ""
    phone = ""

    for x in card.select(".kingster-personnel-info-list"):
        txt = clean(x.get_text())
        cls = " ".join(x.get("class", []))
        if "office" in cls:
            office = txt.replace("Office:", "").strip()
        elif "email" in cls:
            email = txt
        elif "phone" in cls:
            phone = txt

    research = []
    cont = card.select_one(".gdlr-core-personnel-list-content")
    if cont:
        research = split_research(cont.get_text())

    records.append({
        "name": name,
        "designation": des,
        "office": office,
        "email": email,
        "phone": phone,
        "research": research,
        "profile": profile,
        "image": img,
    })

print(f"Extracted: {len(records)} faculty")
for r in records[:10]:
    print(f"{r['name']} | {r['designation']} | {r['email']}")

saved = save(records)
print(f"Saved {saved}/{len(records)} faculty")
def main():
    ...

if __name__ == "__main__":
    main()