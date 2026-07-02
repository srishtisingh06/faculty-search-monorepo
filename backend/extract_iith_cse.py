import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

with open('data/raw/iith_cse.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
h3_tags = soup.find_all('h3')

DESIGNATION_KEYWORDS = ['Professor', 'Head', 'Assistant', 'Associate', 'Dean']
SECTION_HEADERS = ['Regular Faculty', 'Visiting Faculty', 'Adjunct Faculty', 'Emeritus Faculty', 'Former Faculty']

records = []
for h3 in h3_tags:
    name = h3.get_text(strip=True)
    if not name or name in SECTION_HEADERS:
        continue

    designation = ''
    h4 = h3.find_next_sibling('h4')
    if not h4:
        h4 = h3.find_next('h4')
    if h4:
        designation = h4.get_text(strip=True)

    # collect the h5 tags between this h3 and the next h3
    h5_texts = []
    node = h3.find_next_sibling()
    hops = 0
    while node and hops < 8:
        if node.name == 'h3':
            break
        if node.name == 'h5':
            h5_texts.append(node.get_text(strip=True))
        node = node.find_next_sibling()
        hops += 1

    email = ''
    phone = ''
    office = ''
    research_text = ''
    for t in h5_texts:
        if '@' in t:
            email = t
        elif re.search(r'\+?\d{3,}', t) and len(t) < 20:
            phone = t
        elif not office and len(t) < 25 and ('-' in t or t.isupper() or any(c.isdigit() for c in t)):
            office = t
        else:
            if not research_text:
                research_text = t

    research_list = [r.strip() for r in research_text.split(',') if r.strip()][:6]

    records.append({
        'name': name,
        'designation': designation,
        'email': email,
        'phone': phone,
        'office': office,
        'research_areas': research_list,
    })

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
