from bs4 import BeautifulSoup

with open('data/raw/iith_cse.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print(f'Total HTML size: {len(html)}')

headings = soup.find_all(['h1','h2','h3','h4','h5','h6'])
print(f'\nHeadings: {len(headings)}')
for h in headings[:15]:
    print(f'  {h.name}: {h.get_text().strip()[:60]}')

# Check common card/container class patterns
for cls in ['faculty-card', 'MuiPaper-root', 'card', 'faculty-item', 'team-member', 'person', 'profile-card', 'elementor-widget']:
    found = soup.find_all(class_=cls)
    if found:
        print(f'\nElements with class "{cls}": {len(found)}')

# Count images (often anchor faculty entries)
imgs = soup.find_all('img')
print(f'\nTotal <img> tags: {len(imgs)}')

# Check for mailto links (usually one per faculty)
mailtos = soup.find_all('a', href=lambda h: h and h.startswith('mailto:'))
print(f'mailto links: {len(mailtos)}')
if mailtos:
    print('Sample mailto hrefs:', [a["href"] for a in mailtos[:5]])

# Check for common faculty designation keywords in text
text = soup.get_text(' ', strip=True)
print(f'\n"Professor" occurrences: {text.count("Professor")}')
print(f'"Assistant Professor" occurrences: {text.count("Assistant Professor")}')
