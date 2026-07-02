from bs4 import BeautifulSoup
 
with open('data/raw/iitr_cse.html', encoding='utf-8') as f:
    html = f.read()
 
soup = BeautifulSoup(html, 'lxml')
 
headings = soup.find_all(['h1','h2','h3','h4','h5'])
print(f'Headings: {len(headings)}')
for h in headings[:15]:
    print(f'  {h.name}: {h.get_text().strip()[:60]}')
 
# Look for "READ MORE" links which seemed to mark each faculty card
read_more = soup.find_all('a', string=lambda s: s and 'READ MORE' in s.upper())
print(f'\n"READ MORE" links found: {len(read_more)}')
if read_more:
    print('Sample href:', read_more[0].get('href'))
    parent = read_more[0].find_parent(['div', 'li', 'article'])
    if parent:
        print('\nSample card text:')
        print(parent.get_text(' ', strip=True)[:400])
 
# email pattern check
import re
text = soup.get_text(' ', strip=True)
emails = re.findall(r'[\w.\-]+\[at\][\w.\-]+', text)
print(f'\nEmails ([at] format) found: {len(emails)}')
print(emails[:5])