from bs4 import BeautifulSoup

with open('data/raw/iitb_me.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Saara visible text dekho first 2000 chars
body_text = soup.get_text(' ', strip=True)
print(body_text[:2000])
