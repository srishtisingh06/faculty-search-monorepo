import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

URL = 'https://old.iitbbs.ac.in/school-people-faculty.php?code=ms'
DESIGNATIONS = ['Assistant Professor', 'Associate Professor', 'Professor', 'Assistant professor']
EMAIL_RE = re.compile(r'([\w.\-]+@iitbbs\.ac\.in)')
PHONE_RE = re.compile(r'Tel:\s*([+\d,\s\-]{6,}?)(?=Research Interests|Dr\.|Prof\.|$)')


async def fetch():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        print(f'Fetching: {URL}')
        await page.goto(URL, wait_until='domcontentloaded', timeout=45000)
        await page.wait_for_timeout(6000)
        html = await page.content()
        with open('data/raw/iitbbs_me.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Saved! Size: {len(html)}')
        await browser.close()


def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def extract_and_save():
    with open('data/raw/iitbbs_me.html', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'lxml')
    text = soup.get_text(' ', strip=True)

    chunks = re.split(r'(?=(?:Dr\.|Prof\.)\s)', text)
    records = []
    seen = set()

    for chunk in chunks:
        chunk = chunk.strip()
        if not (chunk.startswith('Dr.') or chunk.startswith('Prof.')) or len(chunk) < 15:
            continue

        m = re.match(r'(?:Dr\.|Prof\.)\s+([A-Za-z.\s]+?)\s+(?=Assistant Professor|Associate Professor|Professor|Head,)', chunk)
        if not m:
            continue
        name = m.group(1).strip()
        if name in seen or len(name) < 3:
            continue
        seen.add(name)

        designation = ''
        for d in DESIGNATIONS:
            if d in chunk:
                designation = d
                break

        email_m = EMAIL_RE.search(chunk)
        email = email_m.group(1) if email_m else ''

        phone_m = PHONE_RE.search(chunk)
        phone = phone_m.group(1).strip() if phone_m else ''

        research = ''
        if 'Research Interests:' in chunk:
            research = chunk.split('Research Interests:', 1)[1]
        research_list = [r.strip().rstrip('.') for r in research.split(',') if r.strip()][:6]
        research_list = [r for r in research_list if len(r) > 2][:6]

        records.append({
            'name': name,
            'designation': designation or 'Faculty',
            'email': email,
            'phone': phone,
            'research_areas': research_list,
        })

    print(f'Extracted: {len(records)} ME faculty')
    for r in records:
        print(f"  {r['name']} | {r['designation']} | {r['email']}")

    saved = 0
    for r in records:
        slug = slugify(r['name'])
        profile_url = f'https://old.iitbbs.ac.in/school-people-faculty.php?code=ms#{slug}'
        profile = {
            'faculty_name': r['name'],
            'designation': r['designation'],
            'email': r['email'],
            'phone': r['phone'],
            'research_interests': r['research_areas'],
            'profile_url': profile_url,
            'institute_name': 'IIT Bhubaneswar',
            'institute_type': 'IIT',
            'department': 'Mechanical Engineering',
        }
        ok = save_faculty_profile(
            profile,
            institute_url='https://www.iitbbs.ac.in',
            institute_type='IIT',
            city='Bhubaneswar',
            state='Odisha'
        )
        if ok:
            saved += 1

    print(f'Saved {saved}/{len(records)} ME faculty to PostgreSQL!')


if __name__ == '__main__':
    asyncio.run(fetch())
    extract_and_save()
