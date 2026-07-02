from bs4 import BeautifulSoup

with open("data/raw/iith_mae.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

print("H1:", len(soup.find_all("h1")))
print("H2:", len(soup.find_all("h2")))
print("H3:", len(soup.find_all("h3")))
print("H4:", len(soup.find_all("h4")))

print("\nClasses:\n")

classes = {}

for tag in soup.find_all(True):
    cls = tag.get("class")
    if cls:
        for c in cls:
            classes[c] = classes.get(c, 0) + 1

for k, v in sorted(classes.items(), key=lambda x: -x[1])[:50]:
    print(v, k)