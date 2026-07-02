from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile

with open('data/raw/iitb_ee.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

seen_names = set()
faculty_data = []

for h5 in soup.find_all('h5'):
    name = h5.get_text().strip()
    if not name or len(name) < 3 or name in seen_names:
        continue
    seen_names.add(name)

    parent = h5.find_parent('a') or (h5.find_parent().find('a', href=True) if h5.find_parent() else None)
    profile_url = parent['href'] if parent and parent.get('href') else ''

    research = ''
    next_el = h5.find_next(['p', 'div'])
    if next_el:
        research = next_el.get_text(strip=True)[:300]

    # Agar profile_url khali hai, naam se unique URL banao
    if not profile_url or profile_url.strip() == '':
        name_slug = name.lower().replace(' ', '-').replace('.', '')
        profile_url = f"https://www.ee.iitb.ac.in/faculty/{name_slug}"

    faculty_data.append({
        'faculty_name': name,
        'designation': 'Professor',
        'email': '',
        'phone': '',
        'research_interests': [r.strip() for r in research.split(',') if r.strip()][:5],
        'profile_url': profile_url,
        'institute_name': 'IIT Bombay',
        'institute_type': 'IIT',
        'department': 'Electrical Engineering',
    })

print(f'Faculty extracted: {len(faculty_data)}')

saved = 0
for profile in faculty_data:
    ok = save_faculty_profile(
        profile,
        institute_url='https://www.ee.iitb.ac.in',
        institute_type='IIT',
        city='Mumbai',
        state='Maharashtra'
    )
    if ok:
        saved += 1

print(f'Saved {saved}/{len(faculty_data)} IIT Bombay Electrical faculty to PostgreSQL!')