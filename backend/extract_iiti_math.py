import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

with open('data/raw/iiti_math.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
widgets = soup.find_all(class_='elementor-widget-text-editor')

DESIGNATIONS = ['Assistant Professor', 'Associate Professor', 'Professor', 'Head']
EMAIL_RE = re.compile(r'([\w.\-]+@iiti\.ac\.in)')
PHONE_RE = re.compile(r'Phone:-?\s*([+\d\s\-Extn.]{6,}?)(?=Room|Research|$)')

records = []
seen = set()

for w in widgets:
    text = w.get_text(' ', strip=True)
    if not (text.startswith('Dr.') or text.startswith('Prof.')):
        continue

    m = re.match(r'(?:Dr\.|Prof\.)\s+([A-Za-z.\s]+?)\s+(?=Assistant Professor|Associate Professor|Professor|Head)', text)
    if not m:
        continue
    name = m.group(1).strip()
    if name in seen or len(name) < 3:
        continue
    seen.add(name)

    designation = ''
    for d in DESIGNATIONS:
        if d in text:
            designation = d
            break

    email_m = EMAIL_RE.search(text)
    email = email_m.group(1) if email_m else ''

    phone_m = PHONE_RE.search(text)
    phone = phone_m.group(1).strip() if phone_m else ''

    research = ''
    if 'Research Area:' in text:
        research = text.split('Research Area:', 1)[1]
    elif 'Research Interest' in text:
        research = text.split('Research Interest', 1)[1].lstrip(':s ')
    research_list = [r.strip() for r in research.split(',') if r.strip()][:6]

    records.append({
        'name': name,
        'designation': designation or 'Faculty',
        'email': email,
        'phone': phone,
        'research_areas': research_list,
    })

print(f'Extracted: {len(records)} Math faculty')
for r in records:
    print(f"  {r['name']} | {r['designation']} | {r['email']}")

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

saved = 0
for r in records:
    slug = slugify(r['name'])
    profile_url = f'https://math.iiti.ac.in/faculty/#{slug}'
    profile = {
        'faculty_name': r['name'],
        'designation': r['designation'],
        'email': r['email'],
        'phone': r['phone'],
        'research_interests': r['research_areas'],
        'profile_url': profile_url,
        'institute_name': 'IIT Indore',
        'institute_type': 'IIT',
        'department': 'Mathematics',
    }
    ok = save_faculty_profile(
        profile,
        institute_url='https://www.iiti.ac.in',
        institute_type='IIT',
        city='Indore',
        state='Madhya Pradesh'
    )
    if ok:
        saved += 1

print(f'Saved {saved}/{len(records)} Math faculty to PostgreSQL!')
