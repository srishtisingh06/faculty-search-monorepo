from bs4 import BeautifulSoup
from database.db_writer import get_connection
import uuid

with open('data/raw/iitb_ee.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

conn = get_connection()
cur = conn.cursor()

updated = 0
seen_names = set()

for h5 in soup.find_all('h5'):
    name = h5.get_text().strip()
    if not name or len(name) < 3 or name in seen_names:
        continue
    seen_names.add(name)

    # Research area dhundo - "Area:" text ke baad
    research = ''
    parent_block = h5.find_parent('div')
    if parent_block:
        block_text = parent_block.get_text(' ', strip=True)
        if 'Area:' in block_text:
            research = block_text.split('Area:', 1)[1][:300]
        elif 'Area of Interests:' in block_text:
            research = block_text.split('Area of Interests:', 1)[1][:300]

    if not research:
        continue

    interests = [r.strip() for r in research.split(',') if r.strip() and len(r.strip()) > 3][:6]
    if not interests:
        continue

    # Find this faculty in DB
    cur.execute("SELECT id FROM faculty WHERE faculty_name = %s AND profile_url LIKE %s", (name, '%ee.iitb%'))
    row = cur.fetchone()
    if not row:
        continue

    faculty_id = row['id']
    for interest in interests:
        cur.execute("""
            INSERT INTO research_interests (id, faculty_id, interest_text, source)
            VALUES (%s, %s, %s, 'research_interests')
            ON CONFLICT (faculty_id, interest_text) DO NOTHING
        """, (str(uuid.uuid4()), faculty_id, interest))
    updated += 1

conn.commit()
print(f"Updated research interests for {updated} faculty")
cur.close()
conn.close()