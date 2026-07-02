from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile
import re

with open('data/raw/iitb_me.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Saare divs dekho jisme phone number pattern ho ya "Prof." se shuru ho
all_text_blocks = soup.find_all(['div', 'tr', 'li'])

faculty_data = []
seen_names = set()

# Regex: "Prof. NAME" pattern dhundo
text = soup.get_text(' ', strip=True)

# Split on "Prof." to get individual faculty blocks
chunks = re.split(r'(?=Prof\.\s)', text)

for chunk in chunks:
    chunk = chunk.strip()
    if not chunk.startswith('Prof.') or len(chunk) < 20:
        continue

    # Name = words right after "Prof." until designation keyword
    m = re.match(r'Prof\.\s+([A-Za-z.\s]+?)\s+(Assistant Professor|Associate Professor|Professor)', chunk)
    if not m:
        continue

    name = m.group(1).strip()
    designation = m.group(2).strip()

    if name in seen_names or len(name) < 3:
        continue
    seen_names.add(name)

    phone_m = re.search(r'(\(\+91\)[\d\-\s)]+\d)', chunk)
    phone = phone_m.group(1) if phone_m else ''

    # Research interests - text after phone or after designation+location
    research_text = chunk[m.end():]
    research_text = re.sub(r'^[\w\s,.\-()+]*?Department\s*', '', research_text)
    if phone:
        research_text = research_text.split(phone)[-1]
    research = research_text.strip()[:200]

    name_slug = name.lower().replace(' ', '-').replace('.', '')

    faculty_data.append({
        'faculty_name': name,
        'designation': designation,
        'email': '',
        'phone': phone,
        'research_interests': [r.strip() for r in research.split(',') if r.strip()][:5],
        'profile_url': f'https://www.me.iitb.ac.in/faculty/{name_slug}',
        'institute_name': 'IIT Bombay',
        'institute_type': 'IIT',
        'department': 'Mechanical Engineering',
    })

print(f'Faculty extracted: {len(faculty_data)}')
for f in faculty_data[:5]:
    print(f"  {f['faculty_name']} | {f['designation']} | {f['phone']}")

saved = 0
for profile in faculty_data:
    ok = save_faculty_profile(
        profile,
        institute_url='https://www.me.iitb.ac.in',
        institute_type='IIT',
        city='Mumbai',
        state='Maharashtra'
    )
    if ok:
        saved += 1

print(f'\nSaved {saved}/{len(faculty_data)} IIT Bombay Mechanical faculty to PostgreSQL!')