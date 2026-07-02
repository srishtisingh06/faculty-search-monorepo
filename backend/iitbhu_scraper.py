"""
Reusable IIT (BHU) Varanasi faculty scraper.
Works for CSE, ME, EE, ECE, Math (Drupal-based site, consistent template).
"""
import argparse
import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

DESIGNATIONS = ['Professor & HoD', 'Professor & HOD', 'Professor (HAG)', 'Professor Emeritus',
                'Associate Professor', 'Assistant Professor', 'Professor']
EMAIL_RE = re.compile(r'([\w.\-]+)\s*(?:@|\[at\])\s*([\w.\-]+\.(?:ac\.in|in|com))', re.IGNORECASE)
PHONE_RE = re.compile(r'(\+?\d[\d\-\s]{7,}\d)')


async def fetch(url, out_path):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        print(f'Fetching: {url}')
        await page.goto(url, wait_until='domcontentloaded', timeout=45000)
        await page.wait_for_timeout(6000)
        html = await page.content()
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Saved! Size: {len(html)} -> {out_path}')
        await browser.close()


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def extract(html_path):
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    full_text = soup.get_text(' ', strip=True)
    start_marker = 'Faculty Members'
    end_marker = 'Employee Login'
    start_idx = full_text.find(start_marker)
    end_idx = full_text.find(end_marker)
    if start_idx != -1:
        full_text = full_text[start_idx:]
    if end_idx != -1 and end_idx > start_idx:
        full_text = full_text[:end_idx - start_idx] if start_idx != -1 else full_text[:end_idx]

    chunks = re.split(r'(?=(?:Dr\.|Prof\.)\s)', full_text)
    records = []
    seen = set()

    for chunk in chunks:
        chunk = chunk.strip()
        if not (chunk.startswith('Dr.') or chunk.startswith('Prof.')) or len(chunk) < 10:
            continue

        cut_idx = len(chunk)
        for d in DESIGNATIONS:
            idx = chunk.find(d)
            if idx != -1 and idx < cut_idx:
                cut_idx = idx
        email_search = EMAIL_RE.search(chunk)
        if email_search and email_search.start() < cut_idx:
            cut_idx = email_search.start()
        phone_search = PHONE_RE.search(chunk)
        if phone_search and phone_search.start() < cut_idx:
            cut_idx = phone_search.start()

        name_raw = chunk[:cut_idx].strip()
        name = re.sub(r'^(Dr\.|Prof\.)\s*', '', name_raw).strip(' .-')

        if not name or len(name) < 3 or len(name) > 50 or name in seen:
            continue
        seen.add(name)

        designation = ''
        for d in DESIGNATIONS:
            if d in chunk:
                designation = d
                break

        email = ''
        email_m = EMAIL_RE.search(chunk)
        if email_m:
            email = f"{email_m.group(1)}@{email_m.group(2)}"

        phone = ''
        phone_m = PHONE_RE.search(chunk)
        if phone_m:
            phone = phone_m.group(1).strip()

        # capture leftover "specialization" text between name-cut and phone/email
        # as a fallback research interest when no "Area of Interest:" present
        research_list = []
        if 'Area of Interest:' in chunk:
            research_text = chunk.split('Area of Interest:', 1)[1][:300]
            research_list = [r.strip() for r in research_text.split(',') if r.strip() and r.strip() != '-'][:6]
        elif not designation and not email:
            # Adjunct-style entry: leftover text between name and phone is the specialization
            leftover = chunk[cut_idx:phone_m.start()].strip() if phone_m else ''
            if leftover:
                research_list = [leftover]
                designation = 'Adjunct Faculty'

        records.append({
            'name': name,
            'designation': designation or 'Faculty',
            'email': email,
            'phone': phone,
            'research_areas': research_list,
        })

    return records


def save(records, institute, department, url, city, state, inst_type):
    seen_urls = set()
    saved = 0
    for r in records:
        slug = slugify(r['name'])
        profile_url = f"{url}#{slug}"
        if profile_url in seen_urls:
            profile_url = f"{profile_url}-{slugify(r['email'] or r['name'])}"
        seen_urls.add(profile_url)

        profile = {
            'faculty_name': r['name'],
            'designation': r['designation'],
            'email': r['email'],
            'phone': r['phone'],
            'research_interests': r['research_areas'],
            'profile_url': profile_url,
            'institute_name': institute,
            'institute_type': inst_type,
            'department': department,
        }
        ok = save_faculty_profile(
            profile,
            institute_url='https://www.iitbhu.ac.in',
            institute_type=inst_type,
            city=city,
            state=state
        )
        if ok:
            saved += 1
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', required=True)
    ap.add_argument('--html', required=True)
    ap.add_argument('--department', required=True)
    ap.add_argument('--institute', default='IIT (BHU) Varanasi')
    ap.add_argument('--city', default='Varanasi')
    ap.add_argument('--state', default='Uttar Pradesh')
    ap.add_argument('--type', default='IIT')
    ap.add_argument('--skip-fetch', action='store_true')
    args = ap.parse_args()

    if not args.skip_fetch:
        asyncio.run(fetch(args.url, args.html))

    records = extract(args.html)
    print(f'\nExtracted: {len(records)} faculty')
    for r in records:
        print(f"  {r['name']} | {r['designation']} | {r['email']}")

    saved = save(records, args.institute, args.department, args.url, args.city, args.state, args.type)
    print(f'\nSaved {saved}/{len(records)} to PostgreSQL!')


if __name__ == '__main__':
    main()
