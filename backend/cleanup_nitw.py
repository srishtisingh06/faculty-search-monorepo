from database.db_writer import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("DELETE FROM faculty WHERE institute_id = (SELECT id FROM institutes WHERE name = 'NIT Warangal')")
conn.commit()
print(f"Deleted {cur.rowcount} records")
cur.close()
conn.close()