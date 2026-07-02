import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host="localhost",
    database="faculty_search",
    user="postgres",
    password="Sri2866"   # <-- apna password
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Canonical institute (www.iitbbs.ac.in)
CANONICAL_ID = "f0c97bbd-e03e-4422-8e67-d6bb4791b03b"

OLD_IDS = [
    "03fb1204-4338-426e-84ab-0aeb5168c328",
    "364242ba-a87e-40a1-8c2e-c5e821884f12"
]

for old_id in OLD_IDS:

    print(f"\nProcessing {old_id}")

    # Departments under duplicate institute
    cur.execute("""
        SELECT id, canonical_name
        FROM departments
        WHERE institute_id=%s
    """, (old_id,))

    old_departments = cur.fetchall()

    for dept in old_departments:

        old_dept = dept["id"]
        canonical_name = dept["canonical_name"]

        # Does department already exist under canonical institute?
        cur.execute("""
            SELECT id
            FROM departments
            WHERE institute_id=%s
            AND canonical_name=%s
        """, (CANONICAL_ID, canonical_name))

        existing = cur.fetchone()

        if existing:

            new_dept = existing["id"]

        else:

            cur.execute("""
                UPDATE departments
                SET institute_id=%s
                WHERE id=%s
            """, (CANONICAL_ID, old_dept))

            new_dept = old_dept

        # Move faculty
        cur.execute("""
            UPDATE faculty
            SET
                institute_id=%s,
                department_id=%s
            WHERE
                institute_id=%s
                AND department_id=%s
        """, (
            CANONICAL_ID,
            new_dept,
            old_id,
            old_dept
        ))

        # Delete duplicate department if merged
        if existing:

            cur.execute("""
                DELETE FROM departments
                WHERE id=%s
            """, (old_dept,))

    # Delete duplicate institute
    cur.execute("""
        DELETE FROM institutes
        WHERE id=%s
    """, (old_id,))

conn.commit()

print("\nCleanup completed successfully!")

cur.close()
conn.close()