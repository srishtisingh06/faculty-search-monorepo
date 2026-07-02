from bs4 import BeautifulSoup

with open("data/raw/iith_mae.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

card = soup.find("div", class_="card")

print(card.prettify()[:6000])