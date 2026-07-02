from bs4 import BeautifulSoup

with open("data/raw/iith_ai.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

containers = soup.find_all("div", attrs={"data-element_type": "container"})

print("Total containers:", len(containers))

for c in containers:
    names = c.find_all("h4")
    if names:
        print("=" * 70)
        print("H4 count:", len(names))
        print("First names:")
        for h in names[:5]:
            print("-", h.get_text(strip=True))