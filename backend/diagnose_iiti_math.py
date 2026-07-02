from bs4 import BeautifulSoup

with open('data/raw/iiti_math.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
print(f'Total HTML size: {len(html)}')

headings = soup.find_all(['h1','h2','h3','h4','h5','h6'])
print(f'\nHeadings: {len(headings)}')
for h in headings[:15]:
    print(f'  {h.name}: {h.get_text().strip()[:60]}')

for cls in ['faculty-card', 'MuiPaper-root', 'card', 'faculty-item', 'team-member', 'person', 'profile-card', 'elementor-widget', 'faculty']:
    found = soup.find_all(class_=cls)
    if found:
        print(f'\nElements with class "{cls}": {len(found)}')

imgs = soup.find_all('img')
print(f'\nTotal <img> tags: {len(imgs)}')

mailtos = soup.find_all('a', href=lambda h: h and h.startswith('mailto:'))
print(f'mailto links: {len(mailtos)}')
if mailtos:
    print('Sample:', [a["href"] for a in mailtos[:5]])
