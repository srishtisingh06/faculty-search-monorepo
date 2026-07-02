from bs4 import BeautifulSoup

with open('data/raw/iiti_math.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Look at widget types
widgets = soup.find_all(class_='elementor-widget')
widget_types = {}
for w in widgets:
    for c in w.get('class', []):
        if c.startswith('elementor-widget-') and c != 'elementor-widget':
            widget_types[c] = widget_types.get(c, 0) + 1
print('Widget types:')
for wt, count in widget_types.items():
    print(f'  {wt}: {count}')

# Look at the full text near the first image (likely first faculty)
imgs = soup.find_all('img')
if imgs:
    img = imgs[5]  # skip first few which might be logos
    print('\n--- Text around image 5 ---')
    parent = img
    for level in range(6):
        parent = parent.parent
        if parent is None:
            break
        txt = parent.get_text(' ', strip=True)
        if len(txt) > 20:
            print(f'Level {level} ({parent.name}, class={parent.get("class")}): {txt[:400]}')
            print()
