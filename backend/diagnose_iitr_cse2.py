from bs4 import BeautifulSoup
 
with open('data/raw/iitr_cse.html', encoding='utf-8') as f:
    html = f.read()
 
soup = BeautifulSoup(html, 'lxml')
cards = soup.find_all('div', class_='faculty-card')
print(f'Total faculty-card divs: {len(cards)}')
 
card = cards[0]
print('\n--- Full tag structure of first card ---')
print(card.prettify()[:2000])
 