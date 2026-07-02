"""
Extract + save IIT Roorkee faculty (works for any department using the same
Channel-i 'faculty-card' template — CSE confirmed, likely reusable for ME/EE/ECE/Math).
"""
import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile
 
PHONE_RE = re.compile(r'(\+?\d[\d\-\s]{7,}\d)')
 
 
def extract_faculty(html):
    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all('div', class_='faculty-card')
    records = []
 
    for card in cards:
        name_div = card.select_one('.name .intro-text')
        name = name_div.get_text(strip=True) if name_div else ''
        if not name:
            continue
 
        desig_div = card.select_one('.designation .intro-text-light')
        designation = desig_div.get_text(strip=True) if desig_div else ''
 
        email = ''
        phone = ''
        for info in card.find_all('div', class_='info-content'):
            icon_img = info.find('img', attrs={'data-icon': True})
            icon_type = icon_img.get('data-icon') if icon_img else None
            val_div = info.select_one('.intro-text')
            val = val_div.get_text(strip=True) if val_div else ''
            if icon_type == 'email':
                email = val.replace('[at]', '@')
            elif icon_type == 'phone':
                phone = val
 
        desc_div = card.select_one('.body .description')
        research_text = desc_div.get_text(' ', strip=True) if desc_div else ''
        research_list = [r.strip() for r in research_text.split(',') if r.strip()][:6]
 
        link_tag = card.select_one('.link-content')
        profile_url = link_tag.get('href', '') if link_tag else ''
 
        records.append({
            'name': name,
            'designation': designation,
            'email': email,
            'phone': phone,
            'research_areas': research_list,
            'profile_url': profile_url,
        })
 
    return records
 
 
def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')
 
 
def save_records(records, department, listing_url):
    saved = 0
    seen_urls = set()
    for r in records:
        profile_url = r['profile_url']
        if not profile_url:
            profile_url = f"{listing_url}#{slugify(r['name'])}"
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
            'institute_name': 'IIT Roorkee',
            'institute_type': 'IIT',
            'department': department,
        }
        ok = save_faculty_profile(
            profile,
            institute_url='https://iitr.ac.in',
            institute_type='IIT',
            city='Roorkee',
            state='Uttarakhand'
        )
        if ok:
            saved += 1
    return saved
 
 
if __name__ == '__main__':
    with open('data/raw/iitr_cse.html', encoding='utf-8') as f:
        html = f.read()
 
    records = extract_faculty(html)
    print(f'Extracted: {len(records)} CSE faculty')
    for r in records[:5]:
        print(f"  {r['name']} | {r['designation']} | {r['email']}")
 
    saved = save_records(
        records, 'Computer Science & Engineering',
        'https://iitr.ac.in/Departments/Computer%20Science%20and%20Engineering%20Department/People/Faculty/index.html'
    )
    print(f'Saved {saved}/{len(records)} to PostgreSQL!')