#!/usr/bin/env python3
"""
Reusable Material UI faculty extractor (FIXED).
Adapted for Material UI layouts (e.g. IIT Indore EE).
 
Usage:
  python extract_mui_fixed.py --html data/raw/iiti_ee.html --institute "IIT Indore" \
      --department "Electrical Engineering" --url https://ee.iiti.ac.in/people/faculty \
      --city Indore --state "Madhya Pradesh" --type IIT
"""
 
import argparse
import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile
 
 
def text(el):
    return el.get_text(" ", strip=True) if el else ""
 
 
def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')
 
 
def extract(html_path):
    soup = BeautifulSoup(open(html_path, encoding="utf-8").read(), "html.parser")
    cards = [c for c in soup.select(".MuiPaper-root") if c.select_one("h6")]
    seen = set()
    profiles = []
 
    for card in cards:
        profile = {
            "faculty_name": "",
            "qualification": "",
            "designation": "",
            "additional_role": "",
            "research_areas": [],
            "phone": "",
            "email": "",
            "office": "",
            "website": "",
            "image": "",
        }
 
        typos = card.select(".MuiTypography-root")
        if typos:
            profile["faculty_name"] = text(typos[0])
            for t in typos[1:]:
                s = text(t)
                l = s.lower()
                if "prof" in l or "assistant" in l or "associate" in l:
                    profile["designation"] = s
                elif profile["qualification"] == "":
                    profile["qualification"] = s
                elif "research focus" in l:
                    research_text = s.split(":", 1)[-1].strip()
                    profile["research_areas"] = [r.strip() for r in research_text.split(',') if r.strip()][:6]
                elif "office" in l:
                    profile["office"] = s.split(":", 1)[-1].strip()
                elif "phone" in l or "tel" in l:
                    profile["phone"] = s.split(":", 1)[-1].strip()
                elif "email" in l:
                    profile["email"] = s.split(":", 1)[-1].strip()
                else:
                    if not profile["additional_role"]:
                        profile["additional_role"] = s
 
        if not profile["faculty_name"] or profile["faculty_name"] in seen:
            continue
        seen.add(profile["faculty_name"])
 
        for a in card.select("a.MuiLink-root"):
            href = a.get("href", "")
            if href.startswith("mailto:"):
                profile["email"] = href.replace("mailto:", "")
            elif href.startswith("http"):
                profile["website"] = href
 
        for p in card.select("p"):
            s = text(p)
            if "+91" in s or "Extn" in s:
                profile["phone"] = s
            if "Pod" in s or "Room" in s:
                profile["office"] = s
 
        img = card.select_one("img")
        if img:
            profile["image"] = img.get("src", "")
 
        profiles.append(profile)
 
    return profiles
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--institute", required=True)
    ap.add_argument("--department", required=True)
    ap.add_argument("--url", default="")
    ap.add_argument("--city", default="")
    ap.add_argument("--state", default="")
    ap.add_argument("--type", default="IIT")
    args = ap.parse_args()
 
    records = extract(args.html)
    print(f'Extracted: {len(records)} faculty')
    for r in records[:5]:
        print(f"  {r['faculty_name']} | {r['designation']} | {r['email']}")
 
    seen_urls = set()
    saved = 0
    for p in records:
        # Build a proper, UNIQUE profile_url — critical because the DB column
        # is UNIQUE + NOT NULL. Prefer real website link, else email, else a
        # slug fallback anchored to the listing page URL.
        profile_url = p.get('website', '')
        if not profile_url:
            slug = slugify(p['faculty_name'])
            profile_url = f"{args.url}#{slug}" if args.url else f"https://unknown-source#{slug}"
        if profile_url in seen_urls:
            profile_url = f"{profile_url}-{slugify(p.get('email') or p['faculty_name'])}"
        seen_urls.add(profile_url)
 
        db_profile = {
            'faculty_name': p['faculty_name'],
            'designation': p['designation'] or 'Faculty',
            'email': p['email'],
            'phone': p['phone'],
            'research_interests': p['research_areas'],
            'profile_url': profile_url,
            'institute_name': args.institute,
            'institute_type': args.type,
            'department': args.department,
        }
        ok = save_faculty_profile(
            db_profile,
            institute_url=args.url,
            institute_type=args.type,
            city=args.city,
            state=args.state,
        )
        if ok:
            saved += 1
 
    print(f'Saved {saved}/{len(records)} to PostgreSQL!')
 
 
if __name__ == "__main__":
    main()