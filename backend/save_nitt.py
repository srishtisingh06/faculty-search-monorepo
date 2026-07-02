from extraction.pipeline import process_page
from database.db_writer import save_faculty_profile

with open('data/raw/nitt_page.html', encoding='utf-8') as f:
    html = f.read()

records = process_page(html, source_url='https://nitt.edu/home/academics/departments/faculty/')

saved = 0
for r in records:
    # Map extraction schema to your existing DB schema
    profile = {
        'faculty_name': r['name'],
        'designation': r['designation'],
        'email': r['email'],
        'phone': r['phone'],
        'research_interests': r['research_areas'],
        'profile_url': r['profile_url'] or 'https://nitt.edu/home/academics/departments/faculty/',
        'institute_name': 'NIT Trichy',
        'institute_type': 'NIT',
        'department': '',
    }
    if profile['profile_url'].startswith('/'):
        profile['profile_url'] = 'https://nitt.edu' + profile['profile_url']

    ok = save_faculty_profile(
        profile,
        institute_url='https://nitt.edu',
        institute_type='NIT',
        city='Tiruchirappalli',
        state='Tamil Nadu'
    )
    if ok:
        saved += 1

print(f'Saved {saved}/{len(records)} NIT Trichy faculty to PostgreSQL!')