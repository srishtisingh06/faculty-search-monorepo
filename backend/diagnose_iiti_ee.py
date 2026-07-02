from bs4 import BeautifulSoup

with open('data/raw/iiti_ee.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
cards = [c for c in soup.select(".MuiPaper-root") if c.select_one("h6")]

for card in cards:
    h6 = card.select_one('h6')
    name = h6.get_text(strip=True) if h6 else ''
    if 'Swaminathan' in name or 'Himali' in name:
        print(f'=== Card for: {name} ===')
        for a in card.select('a.MuiLink-root'):
            print(f'  <a> href: {a.get("href")}')
        for p in card.select('p'):
            print(f'  <p>: {p.get_text(strip=True)}')
        print()
