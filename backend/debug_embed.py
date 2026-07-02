from database.db_writer import get_connection
from embeddings.embed_pipeline import build_embed_text

conn = get_connection()
cur = conn.cursor()
cur.execute("""
    SELECT f.id, f.faculty_name, f.designation, d.canonical_name as department
    FROM faculty f
    LEFT JOIN departments d ON f.department_id = d.id
    WHERE f.profile_url LIKE '%ee.iitb%' OR f.profile_url LIKE '%me.iitb%'
    LIMIT 3
""")
rows = cur.fetchall()

for row in rows:
    fid = row['id']
    cur.execute("SELECT interest_text, source FROM research_interests WHERE faculty_id = %s", (fid,))
    interests = cur.fetchall()
    row_dict = dict(row)
    row_dict['research_interests'] = [r['interest_text'] for r in interests if r['source'] == 'research_interests']
    row_dict['research_areas'] = [r['interest_text'] for r in interests if r['source'] == 'research_areas']
    row_dict['biography'] = ''
    row_dict['projects'] = []
    row_dict['publications'] = []
    
    text = build_embed_text(row_dict)
    print(f"{row_dict['faculty_name']}: embed_text = '{text}'")

cur.close()
conn.close()
