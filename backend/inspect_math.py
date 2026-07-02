from bs4 import BeautifulSoup

with open("data/raw/iith_math.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

print("H1:", len(soup.find_all("h1")))
print("H2:", len(soup.find_all("h2")))
print("H3:", len(soup.find_all("h3")))
print("H4:", len(soup.find_all("h4")))

print("\nTop Classes:\n")

classes = {}

for tag in soup.find_all(True):
    cls = tag.get("class")
    if cls:
        for c in cls:
            classes[c] = classes.get(c, 0) + 1

for k, v in sorted(classes.items(), key=lambda x: -x[1])[:50]:
    print(v, k)

print("\nFirst Faculty Card:\n")

card = soup.find("div", class_="gdlr-core-personnel-list")

if card:
   print(card.prettify()[:6000])
    