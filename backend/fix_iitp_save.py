import json
from database.db_writer import save_faculty_profile
from extraction.pipeline import process_page

# Already fetched HTML use karo
with open('data/raw/iitp_me.html', encoding='utf-8') as f:
    html = f.read()

records = process_page(html, source_url='https://me.iitp.ac.in/faculty.html')

saved = 0
for r in records:
    profile = {
        'faculty_name': r['name'],
        'designation': r['designation'],
        'email': r['email'],
        'phone': r['phone'],
        'research_interests': r['research_areas'],
        'profile_url': r['profile_url'] or 'https://me.iitp.ac.in/faculty.html',
        'institute_name': 'IIT Patna',
        'institute_type': 'IIT',
        'department': 'Mechanical Engineering',
    }
    ok = save_faculty_profile(
        profile,
        institute_url='https://me.iitp.ac.in',
        institute_type='IIT',
        city='Patna',
        state='Bihar'
    )
    if ok:
        saved += 1

print(f'Saved {saved}/{len(records)} IIT Patna ME faculty!')