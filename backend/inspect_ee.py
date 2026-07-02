from bs4 import BeautifulSoup

with open("data/raw/iiti_ee.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

print("H1:", len(soup.find_all("h1")))
print("H2:", len(soup.find_all("h2")))
print("H3:", len(soup.find_all("h3")))
print("H4:", len(soup.find_all("h4")))

print("\nTop Classes\n")

classes = {}

for tag in soup.find_all(True):
    cls = tag.get("class")
    if cls:
        for c in cls:
            classes[c] = classes.get(c, 0) + 1

for k, v in sorted(classes.items(), key=lambda x: -x[1])[:50]:
    print(v, k)

print("\n================ FACULTY CARD ================\n")

cards = soup.select(".MuiPaper-root")

print("Total MuiPaper cards:", len(cards))

for i, c in enumerate(cards):
    text = c.get_text(" ", strip=True)

    if "Prof." in text or "Professor" in text or "Assistant Professor" in text or "Associate Professor" in text:
        print("\nFaculty Card Found:", i)
        print(c.prettify()[:8000])
        break