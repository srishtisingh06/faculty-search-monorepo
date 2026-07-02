from bs4 import BeautifulSoup

with open('data/raw/iitb_ee.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Headings dekho
headings = soup.find_all(['h1','h2','h3','h4','h5'])
print(f'Headings: {len(headings)}')
for h in headings[:15]:
    print(f'  {h.name}: {h.get_text().strip()[:60]}')

# Classes dekho jisme "faculty" word ho
faculty_divs = soup.find_all(class_=lambda c: c and 'faculty' in str(c).lower())
print(f'\nFaculty-related divs: {len(faculty_divs)}')
if faculty_divs:
    print(faculty_divs[0].prettify()[:500])