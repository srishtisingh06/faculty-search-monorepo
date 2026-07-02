"""
Diagnostic: inspect the unified IIT Bhubaneswar faculty table structure
to see why ME (Mechanical Sciences) filter only matched 3 rows.
"""
from bs4 import BeautifulSoup
 
with open('data/raw/iitbbs_all.html', encoding='utf-8') as f:
    html = f.read()
 
soup = BeautifulSoup(html, 'lxml')
tables = soup.find_all('table')
print(f'Number of <table> tags found: {len(tables)}')
 
for ti, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f'\nTable {ti}: {len(rows)} rows')
    if rows:
        header_cells = rows[0].find_all(['td', 'th'])
        print('  Header row:', [c.get_text(strip=True) for c in header_cells])
    if len(rows) > 1:
        sample_cells = rows[1].find_all(['td', 'th'])
        print('  Sample row 1:', [c.get_text(strip=True) for c in sample_cells])
 
# Also, count distinct values seen in whatever we guessed is the "School" column (index 2)
if tables:
    main_table = tables[0]
    rows = main_table.find_all('tr')
    school_values = {}
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 3:
            val = cells[2].get_text(strip=True)
            school_values[val] = school_values.get(val, 0) + 1
    print('\nDistinct values in column index 2 (assumed School):')
    for val, count in school_values.items():
        print(f'  "{val}": {count}')