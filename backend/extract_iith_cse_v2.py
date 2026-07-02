import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

with open('data/raw/iith_cse.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Get ALL h3/h4/h5 tags in true document order (ignores nesting/sibling issues)
tags = soup.find_all(['h3', 'h4', 'h5'])

SECTION_HEADERS = ['Regular Faculty', 'Visiting Faculty', 'Adjunct Faculty',
                   'Emeritus Faculty', 'Former Faculty', 'Honorary Faculty', 'Faculty']

records = []
current = None

def flush():
    global current
    if current and current.get('name'):
        records.append(current)
    current = None

for tag in tags:
    txt = tag.get_text(strip=True)
    if not txt:
        continue

    if tag.name == 'h3':
        if txt in SECTION_HEADERS:
            continue
        flush()
        current = {'name': txt, 'designation': '', 'email': '', 'phone': '', 'office': '', 'research_areas': []}
        continue

    if current is None:
        continue

    if tag.name == 'h4':
        current['designation'] = txt
        continue

    if tag.name == 'h5':
        if '@' in txt:
            current['email'] = txt
        elif re.search(r'\+?\d{3,}', txt) and len(txt) < 20:
            current['phone'] = txt
        elif not current['office'] and len(txt) < 20:
            current['office'] = txt
        else:
            current['research_areas'] = [r.strip() for r in txt.split(',') if r.strip()][:6]

flush()

print(f'Extracted: {len(records)} faculty')
for r in records:
    print(f"  {r['name']} | {r['designation']} | {r['email']}")

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

seen_urls = set()
saved = 0
for r in records:
    slug = slugify(r['name'])
    profile_url = f"https://cse.iith.ac.in/people/faculty.html#{slug}"
    if profile_url in seen_urls:
        profile_url = f"{profile_url}-{slugify(r['email'] or r['name'])}"
    seen_urls.add(profile_url)

    profile = {
        'faculty_name': r['name'],
        'designation': r['designation'] or 'Faculty',
        'email': r['email'],
        'phone': r['phone'],
        'research_interests': r['research_areas'],
        'profile_url': profile_url,
        'institute_name': 'IIT Hyderabad',
        'institute_type': 'IIT',
        'department': 'Computer Science & Engineering',
    }
    ok = save_faculty_profile(
        profile,
        institute_url='https://cse.iith.ac.in',
        institute_type='IIT',
        city='Hyderabad',
        state='Telangana'
    )
    if ok:
        saved += 1

print(f'Saved {saved}/{len(records)} to PostgreSQL!')
