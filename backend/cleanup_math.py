from database.db_writer import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
    DELETE FROM faculty 
    WHERE faculty_name IN (
        'Dean, Research and Development (R&D)',
        'Faculty of Biosciences & Biotechnology',
        'Faculty of Interdisciplinary Studies',
        'Faculty of Sciences (FoS)',
        'Vinod Gupta School of Management'
    )
""")
conn.commit()
print(f"Deleted {cur.rowcount} garbage records")
cur.close()
conn.close()