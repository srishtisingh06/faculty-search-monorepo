from bs4 import BeautifulSoup

with open("data/raw/iith_ai.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

print("===== H1 =====")
for h in soup.find_all(["h1","h2","h3","h4"])[:50]:
    t = h.get_text(" ", strip=True)
    if t:
        print(h.name, "->", t)

print("\n===== Faculty Links =====")
count = 0
for a in soup.find_all("a", href=True):
    txt = a.get_text(" ", strip=True)
    href = a["href"]

    if txt and len(txt) > 2:
        if any(x in href.lower() for x in ["faculty", "profile", "people", "author"]):
            print(txt, "->", href)
            count += 1

print("\nFaculty/Profile links found:", count)

print("\n===== Emails =====")
emails = set()

for a in soup.find_all("a", href=True):
    if a["href"].startswith("mailto:"):
        emails.add(a["href"][7:])

for e in sorted(emails):
    print(e)

print("\nTotal emails:", len(emails))