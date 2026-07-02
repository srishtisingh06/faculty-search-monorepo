"""
Generic IIT Roorkee Extractor
Works for CSE, EE, ME, Mathematics
"""
import argparse
import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

# ==========================
# CHANGE ONLY THESE 3 LINES
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

PHONE_RE = re.compile(r'(\+?\d[\d\-\s]{7,}\d)')

def main():
    ...

if __name__ == "__main__":
    main()
def extract_faculty(html):

    soup = BeautifulSoup(html, "lxml")

    cards = soup.find_all("div", class_="faculty-card")

    print(f"Faculty cards found: {len(cards)}")

    records = []

    for card in cards:

        name_div = card.select_one(".name .intro-text")

        name = name_div.get_text(strip=True) if name_div else ""

        if not name:
            continue

        desig_div = card.select_one(".designation .intro-text-light")

        designation = (
            desig_div.get_text(strip=True)
            if desig_div
            else "Faculty"
        )

        email = ""

        phone = ""

        for info in card.find_all("div", class_="info-content"):

            icon = info.find("img", attrs={"data-icon": True})

            icon_type = icon.get("data-icon") if icon else None

            value = info.select_one(".intro-text")

            text = value.get_text(strip=True) if value else ""

            if icon_type == "email":

                email = text.replace("[at]", "@")

            elif icon_type == "phone":

                phone = text

        research = []

        desc = card.select_one(".body .description")

        if desc:

            research = [
                x.strip()
                for x in desc.get_text(" ", strip=True).split(",")
                if x.strip()
            ]

        profile_url = ""

        link = card.select_one(".link-content")

        if link:

            profile_url = link.get("href", "")

        records.append(
            {
                "name": name,
                "designation": designation,
                "email": email,
                "phone": phone,
                "research_areas": research,
                "profile_url": profile_url,
            }
        )

    return records


def slugify(name):

    s = name.lower().strip()

    s = re.sub(r"[^a-z0-9]+", "-", s)

    return s.strip("-")


def save_records(records):

    saved = 0

    seen_urls = set()

    for r in records:

        profile_url = r["profile_url"]

        if not profile_url:

            profile_url = (
                f"{LISTING_URL}#{slugify(r['name'])}"
            )

        if profile_url in seen_urls:

            profile_url = (
                f"{profile_url}-{slugify(r['email'] or r['name'])}"
            )

        seen_urls.add(profile_url)

        profile = {

            "faculty_name": r["name"],

            "designation": r["designation"],

            "email": r["email"],

            "phone": r["phone"],

            "research_interests": r["research_areas"],

            "profile_url": profile_url,

            "institute_name": INSTITUTE_NAME,

            "institute_type": "IIT",

            "department": DEPARTMENT,

        }

        ok = save_faculty_profile(

            profile,

            institute_url=INSTITUTE_URL,

            institute_type="IIT",

            city="Roorkee",

            state="Uttarakhand",

        )

        if ok:

            saved += 1

    return saved


if __name__ == "__main__":

    with open(HTML_FILE, encoding="utf-8") as f:

        html = f.read()

    records = extract_faculty(html)

    print(f"\nExtracted: {len(records)} Faculty\n")

    for r in records[:5]:

        print(
            f"{r['name']} | {r['designation']} | {r['email']}"
        )

    saved = save_records(records)

    print(f"\nSaved {saved}/{len(records)} Faculty Successfully!")