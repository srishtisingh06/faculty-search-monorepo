from bs4 import BeautifulSoup

with open('data/raw/iitb_me.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

headings = soup.find_all(['h1','h2','h3','h4','h5'])
print(f'Headings: {len(headings)}')
for h in headings[:20]:
    print(f'  {h.name}: {h.get_text().strip()[:60]}')

# Links jisme /faculty/ ho
faculty_links = soup.find_all('a', href=lambda h: h and '/faculty/' in h)
print(f'\nFaculty profile links: {len(faculty_links)}')
for a in faculty_links[:10]:
    print(f'  {a.get_text(strip=True)[:40]} -> {a["href"]}')