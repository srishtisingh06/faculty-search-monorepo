"""
Extract + save IIT Roorkee Mechanical Engineering faculty
"""

import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

PHONE_RE = re.compile(r'(\+?\d[\d\-\s]{7,}\d)')


def extract_faculty(html):
    soup = BeautifulSoup(html, "lxml")

    cards = soup.find_all("div", class_="faculty-card")
    print("Faculty cards found:", len(cards))
    records = []

    for card in cards:

        name_div = card.select_one(".name .intro-text")
        name = name_div.get_text(strip=True) if name_div else ""

        if not name:
            continue

        desig_div = card.select_one(".designation .intro-text-light")
        designation = desig_div.get_text(strip=True) if desig_div else ""

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

    LISTING_URL = (
        "https://iitr.ac.in/Departments/"
        "Mechanical%20and%20Industrial%20Engineering%20Department/"
        "People/Faculty/index.html"
    )

    for r in records:

        profile_url = r["profile_url"]

        if not profile_url:
            profile_url = f"{LISTING_URL}#{slugify(r['name'])}"

        if profile_url in seen_urls:
            profile_url = (
                f"{profile_url}-{slugify(r['email'] or r['name'])}"
            )

        seen_urls.add(profile_url)

        profile = {
            "faculty_name": r["name"],
            "designation": r["designation"] or "Faculty",
            "email": r["email"],
            "phone": r["phone"],
            "research_interests": r["research_areas"],
            "profile_url": profile_url,
            "institute_name": "IIT Roorkee",
            "department": "Mechanical Engineering",
        }

        ok = save_faculty_profile(
            profile,
            institute_url="https://iitr.ac.in",
            institute_type="IIT",
            city="Roorkee",
            state="Uttarakhand",
        )

        if ok:
            saved += 1

    return saved


if __name__ == "__main__":

    with open("data/raw/iitr_me.html", encoding="utf-8") as f:
        html = f.read()

    records = extract_faculty(html)
    print("Extracted:", len(records))
    print(f"\nExtracted {len(records)} Mechanical Faculty\n")

    for r in records[:5]:
        print(
            f"{r['name']} | {r['designation']} | {r['email']}"
        )

    saved = save_records(records)

    print(f"\nSaved {saved}/{len(records)} Faculty Successfully!")