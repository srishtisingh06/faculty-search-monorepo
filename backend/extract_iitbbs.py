"""
Extract + save IIT Bhubaneswar faculty: CSE, ECE, EE (from SECS page),
ME (from unified faculty table, filtered by School), Math (from SBS Math page)
Run AFTER fetch_iitbbs.py has saved the 3 HTML files.
"""
import re
from bs4 import BeautifulSoup
from database.db_writer import save_faculty_profile
 
HEADER_TAGS = ['h2', 'h3', 'h4', 'h5', 'h6']
PHONE_RE = re.compile(r'(\+?\d[\d\-\/\(\) ]{6,}\d)')
 
# Maps SECS section headers -> canonical department name
SECS_SECTION_MAP = {
    'Department of Electrical Engineering': 'Electrical Engineering',
    'Department of Electronics & Communication Engineering': 'Electronics & Communication Engineering',
    'Department of Computer Science & Engineering': 'Computer Science & Engineering',
    'Visiting Faculty': 'Computer Science & Engineering',  # appears after CSE section
}
 
 
def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')
 
 
def extract_elementor_faculty_page(html, section_map=None, default_department=None):
    """
    Generic extractor for Elementor-style faculty pages (SECS, SBS Math):
    - headers without a link and matching a known section text -> update current department
    - headers with a link starting 'Dr.'/'Prof.' -> new faculty entry
    - following <ul><li> items -> position / room / phone / email
    - next 'Research Interests' header + following text -> research interests
    """
    soup = BeautifulSoup(html, 'lxml')
    headers = []
    for tag in HEADER_TAGS:
        headers.extend(soup.find_all(tag))
    # sort headers by document order
    headers = sorted(headers, key=lambda h: h.sourceline if h.sourceline is not None else 0)
 
    records = []
    current_department = default_department
    current = None  # in-progress faculty dict
 
    def flush():
        nonlocal current
        if current and current.get('name'):
            records.append(current)
        current = None
 
    i = 0
    all_headers = soup.find_all(HEADER_TAGS)
    for idx, h in enumerate(all_headers):
        text = h.get_text(strip=True)
        link = h.find('a')
 
        if not text:
            continue
 
        # Section header (department name), no link
        if not link and (text.startswith('Department of') or (section_map and text in section_map)):
            if section_map is not None:
                current_department = section_map.get(text, current_department)
            else:
                current_department = text.replace('Department of', '').strip()
            continue
 
        # Research Interests header -> grab following text until next header
        if text == 'Research Interests' and current is not None:
            research_text = ''
            nxt = h.find_next_sibling()
            hops = 0
            while nxt and hops < 3:
                if nxt.name in HEADER_TAGS:
                    break
                t = nxt.get_text(' ', strip=True)
                if t:
                    research_text = t
                    break
                nxt = nxt.find_next_sibling()
                hops += 1
            current['research_areas'] = [r.strip() for r in research_text.split(',') if r.strip()][:6]
            continue
 
        # Faculty name header (has link, starts with Dr./Prof.)
        if link and (text.startswith('Dr.') or text.startswith('Prof.')):
            flush()
            name = text
            designation = ''
            # strip "Head, Department of X" prefix lines handled via first <li>
            current = {
                'name': name,
                'profile_url': link.get('href', ''),
                'department': current_department,
                'designation': '',
                'email': '',
                'phone': '',
                'research_areas': [],
            }
            # gather following <ul> items (position/room/phone/email) before next header
            ul = h.find_next_sibling('ul')
            hops = 0
            node = h.find_next_sibling()
            while node and hops < 5:
                if node.name in HEADER_TAGS:
                    break
                if node.name == 'ul':
                    lis = [li.get_text(' ', strip=True) for li in node.find_all('li')]
                    for li_text in lis:
                        if '@' in li_text:
                            current['email'] = li_text.split()[0].strip()
                        elif PHONE_RE.search(li_text) and 'Room' not in li_text:
                            m = PHONE_RE.search(li_text)
                            current['phone'] = m.group(1).strip()
                        elif not current['designation'] and 'Room' not in li_text and '@' not in li_text:
                            current['designation'] = li_text
                node = node.find_next_sibling()
                hops += 1
            continue
 
    flush()
    return records
 
 
def extract_me_from_unified_table(html, target_school='Mechanical Sciences'):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table')
    records = []
    if not table:
        return records
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 6:
            continue
        name = cells[0].get_text(' ', strip=True)
        position = cells[1].get_text(' ', strip=True)
        school = cells[2].get_text(' ', strip=True)
        contact = cells[3].get_text(' ', strip=True)
        email = cells[4].get_text(' ', strip=True)
        profile_link_tag = cells[5].find('a')
        profile_url = profile_link_tag.get('href', '') if profile_link_tag else ''
 
        if school != target_school:
            continue
        if name in ('Faculty Name', ''):
            continue
 
        phone = ''
        m = PHONE_RE.search(contact)
        if m:
            phone = m.group(1).strip()
 
        email_clean = email.split('/')[0].strip() if email else ''
 
        records.append({
            'name': name,
            'designation': position,
            'email': email_clean,
            'phone': phone,
            'research_areas': [],
            'profile_url': profile_url,
            'department': 'Mechanical Engineering',
        })
    return records
 
 
def save_records(records, institute_name, city, state, institute_url, default_profile_base):
    saved = 0
    seen_urls = set()
    for r in records:
        profile_url = r['profile_url']
        if profile_url.startswith('/'):
            profile_url = institute_url.rstrip('/') + profile_url
        if not profile_url:
            slug = slugify(r['name'])
            profile_url = f"{default_profile_base}#{slug}"
        if profile_url in seen_urls:
            profile_url = f"{profile_url}-{slugify(r.get('email') or r['name'])}"
        seen_urls.add(profile_url)
 
        profile = {
            'faculty_name': r['name'],
            'designation': r.get('designation') or 'Faculty',
            'email': r.get('email', ''),
            'phone': r.get('phone', ''),
            'research_interests': r.get('research_areas', []),
            'profile_url': profile_url,
            'institute_name': institute_name,
            'institute_type': 'IIT',
            'department': r['department'],
        }
        ok = save_faculty_profile(
            profile,
            institute_url=institute_url,
            institute_type='IIT',
            city=city,
            state=state
        )
        if ok:
            saved += 1
    return saved
 
 
def run():
    grand_total = 0
 
    # --- CSE / ECE / EE from SECS page ---
    print('\n=== IIT Bhubaneswar SECS (CSE/ECE/EE) ===')
    with open('data/raw/iitbbs_secs.html', encoding='utf-8') as f:
        secs_html = f.read()
    secs_records = extract_elementor_faculty_page(secs_html, section_map=SECS_SECTION_MAP)
    by_dept = {}
    for r in secs_records:
        by_dept.setdefault(r['department'], []).append(r)
    for dept, recs in by_dept.items():
        print(f'  {dept}: {len(recs)} faculty')
    saved = save_records(
        secs_records, 'IIT Bhubaneswar', 'Bhubaneswar', 'Odisha',
        'https://secs.iitbbs.ac.in', 'https://secs.iitbbs.ac.in/index.php/faculty-members/'
    )
    print(f'Saved {saved}/{len(secs_records)} SECS faculty to PostgreSQL!')
    grand_total += saved
 
    # --- ME from unified table ---
    print('\n=== IIT Bhubaneswar ME (from unified table) ===')
    with open('data/raw/iitbbs_all.html', encoding='utf-8') as f:
        all_html = f.read()
    me_records = extract_me_from_unified_table(all_html)
    print(f'Extracted: {len(me_records)} ME faculty')
    saved = save_records(
        me_records, 'IIT Bhubaneswar', 'Bhubaneswar', 'Odisha',
        'https://www.iitbbs.ac.in', 'https://www.iitbbs.ac.in/index.php/faculty-members/'
    )
    print(f'Saved {saved}/{len(me_records)} ME faculty to PostgreSQL!')
    grand_total += saved
 
    # --- Math from SBS Math page ---
    print('\n=== IIT Bhubaneswar Mathematics ===')
    with open('data/raw/iitbbs_math.html', encoding='utf-8') as f:
        math_html = f.read()
    math_records = extract_elementor_faculty_page(math_html, section_map=None, default_department='Mathematics and Statistics')
    # force department for ALL math records (page covers only math dept, incl. "Visiting Faculty")
    for r in math_records:
        r['department'] = 'Mathematics and Statistics'
    print(f'Extracted: {len(math_records)} Math faculty')
    saved = save_records(
        math_records, 'IIT Bhubaneswar', 'Bhubaneswar', 'Odisha',
        'https://sbs.iitbbs.ac.in', 'https://sbs.iitbbs.ac.in/index.php/mathematics/mathematics-faculty-members/'
    )
    print(f'Saved {saved}/{len(math_records)} Math faculty to PostgreSQL!')
    grand_total += saved
 
    print(f'\n=== TOTAL SAVED (IIT Bhubaneswar, 5 depts): {grand_total} ===')
 
 
if __name__ == '__main__':
    run()
    