"""
Extract + save IIT Kanpur faculty: ME, EE, Mathematics & Statistics (v3)
FIX: unique fallback profile_url per faculty (slug-based) to prevent
     UNIQUE constraint collisions when a faculty has no real profile link.
 
Run this AFTER deleting old ME/EE/Math records for IIT Kanpur (see DELETE below).
"""
import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile
 
DEPTS = {
    'iitk_me': {
        'file': 'data/raw/iitk_me.html',
        'department': 'Mechanical Engineering',
        'has_designation': True,
        'base_url': 'https://www.iitk.ac.in',
        'listing_url': 'https://www.iitk.ac.in/me/people/faculty',
    },
    'iitk_ee': {
        'file': 'data/raw/iitk_ee.html',
        'department': 'Electrical Engineering',
        'has_designation': False,
        'base_url': 'https://www.iitk.ac.in',
        'listing_url': 'https://www.iitk.ac.in/ee/faculty',
    },
    'iitk_math': {
        'file': 'data/raw/iitk_math.html',
        'department': 'Mathematics and Statistics',
        'has_designation': False,
        'base_url': 'https://www.iitk.ac.in',
        'listing_url': 'https://www.iitk.ac.in/math/index.php/faculty',
    },
}
 
DESIGNATIONS = ['Professor', 'Associate Professor', 'Assistant Professor']
PHONE_RE = re.compile(r'(\+?\d[\d\-\/\(\) ]{6,}\d)')
AT_EMAIL_RE = re.compile(r'([\w.\-]+)\s*\[AT\]\s*([\w.\-]+)', re.IGNORECASE)
BAD_NAME_WORDS = {'homepage', 'home page', 'personal homepage', 'irinis profile'}
 
 
def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')
 
 
def get_block_container(img):
    p = img.find_parent('p')
    if p:
        return p
    div = img.find_parent('div')
    return div if div else img.parent
 
 
def extract_name(container, img):
    for a in container.find_all('a'):
        href = a.get('href', '')
        txt = a.get_text(strip=True)
        if 'mailto:' in href:
            continue
        if not txt or len(txt) < 2:
            continue
        if txt.lower() in BAD_NAME_WORDS or 'homepage' in txt.lower():
            continue
        return txt, href
 
    full_text = container.get_text(' ', strip=True)
    for marker in ['PhD', 'Ph.D', '(PhD', 'This email address', '[AT]', '(on leave']:
        idx = full_text.find(marker)
        if idx != -1:
            full_text = full_text[:idx]
            break
    name = full_text.strip(' ,.-')
    for d in DESIGNATIONS:
        if name.endswith(d):
            name = name[: -len(d)].strip(' ,.-')
    return (name if 2 < len(name) < 60 else ''), ''
 
 
def extract_faculty(html, has_designation):
    soup = BeautifulSoup(html, 'lxml')
    imgs = [img for img in soup.find_all('img') if img.get('src') and '/images/faculty/' in img['src']]
 
    records = []
    seen = set()
 
    for img in imgs:
        container = get_block_container(img)
        name, profile_url = extract_name(container, img)
        if not name or name in seen:
            continue
        seen.add(name)
 
        block_text = container.get_text(' ', strip=True)
        if 'Research Interest' not in block_text:
            nxt = container.find_next_sibling()
            hops = 0
            while nxt and hops < 3:
                nxt_text = nxt.get_text(' ', strip=True)
                block_text += ' ' + nxt_text
                if 'Research Interest' in nxt_text:
                    break
                if nxt.find('img', src=lambda s: s and '/images/faculty/' in s):
                    block_text = block_text.rsplit(' ', len(nxt_text.split()))[0]
                    break
                nxt = nxt.find_next_sibling()
                hops += 1
 
        designation = ''
        if has_designation:
            for d in DESIGNATIONS:
                if d in block_text:
                    designation = d
                    break
 
        email = ''
        mailto = container.find('a', href=lambda h: h and h.startswith('mailto:'))
        if mailto:
            email = mailto['href'].replace('mailto:', '').strip()
        else:
            m = AT_EMAIL_RE.search(block_text)
            if m:
                email = f"{m.group(1)}@{m.group(2)}"
 
        phone_m = PHONE_RE.search(block_text)
        phone = phone_m.group(1).strip() if phone_m else ''
 
        research = ''
        if 'Research Interest' in block_text:
            research = block_text.split('Research Interest', 1)[1]
            research = research.lstrip('s:').strip()
        research_list = [r.strip() for r in research.split(',') if r.strip()][:6]
 
        records.append({
            'name': name,
            'designation': designation,
            'email': email,
            'phone': phone,
            'research_areas': research_list,
            'profile_url': profile_url,
        })
 
    return records
 
 
def run():
    grand_total_saved = 0
    for key, cfg in DEPTS.items():
        print(f'\n=== {key} ({cfg["department"]}) ===')
        with open(cfg['file'], encoding='utf-8') as f:
            html = f.read()
 
        records = extract_faculty(html, cfg['has_designation'])
        print(f'Extracted: {len(records)} faculty')
 
        seen_urls = set()
        saved = 0
        for r in records:
            profile_url = r['profile_url']
            if profile_url.startswith('/'):
                profile_url = cfg['base_url'] + profile_url
 
            if not profile_url:
                # UNIQUE fallback per faculty using name slug + listing page anchor
                slug = slugify(r['name'])
                profile_url = f"{cfg['listing_url']}#{slug}"
 
            # extra safety: if somehow still colliding, append email or index
            if profile_url in seen_urls:
                profile_url = f"{profile_url}-{slugify(r['email'] or str(len(seen_urls)))}"
            seen_urls.add(profile_url)
 
            profile = {
                'faculty_name': r['name'],
                'designation': r['designation'] or 'Faculty',
                'email': r['email'],
                'phone': r['phone'],
                'research_interests': r['research_areas'],
                'profile_url': profile_url,
                'institute_name': 'IIT Kanpur',
                'institute_type': 'IIT',
                'department': cfg['department'],
            }
            ok = save_faculty_profile(
                profile,
                institute_url='https://www.iitk.ac.in',
                institute_type='IIT',
                city='Kanpur',
                state='Uttar Pradesh'
            )
            if ok:
                saved += 1
 
        print(f'Saved {saved}/{len(records)} to PostgreSQL!')
        grand_total_saved += saved
 
    print(f'\n=== TOTAL SAVED ACROSS 3 DEPARTMENTS (v3): {grand_total_saved} ===')
 
 
if __name__ == '__main__':
    run()