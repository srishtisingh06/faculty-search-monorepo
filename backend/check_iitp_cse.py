from bs4 import BeautifulSoup

with open('data/raw/iitp_cse.html', encoding='utf-8') as f:
    html = f.read()

print(f'HTML size: {len(html)}')
soup = BeautifulSoup(html, 'lxml')
print(soup.get_text()[:2000])