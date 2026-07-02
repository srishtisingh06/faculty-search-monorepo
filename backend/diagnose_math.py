"""
Diagnostic: figure out why Math faculty extraction undercounts.
Run this and paste the full output.
"""
from bs4 import BeautifulSoup
 
with open('data/raw/iitk_math.html', encoding='utf-8') as f:
    html = f.read()
 
soup = BeautifulSoup(html, 'lxml')
imgs = [img for img in soup.find_all('img') if img.get('src') and '/images/faculty/' in img['src']]
print(f'Total faculty images found: {len(imgs)}')
 
# Check how many unique parent <p> tags
parents = [img.find_parent('p') for img in imgs]
unique_parents = set(id(p) for p in parents if p is not None)
print(f'Unique parent <p> tags: {len(unique_parents)}')
print(f'Images with NO <p> parent: {sum(1 for p in parents if p is None)}')
 
# Show how many images share the same parent (i.e. grouped together)
from collections import Counter
parent_counts = Counter(id(p) for p in parents if p is not None)
multi = {k: v for k, v in parent_counts.items() if v > 1}
print(f'Parent <p> tags containing MORE THAN 1 faculty image: {len(multi)}')
if multi:
    # show first such group's text
    first_id = list(multi.keys())[0]
    for p in parents:
        if p is not None and id(p) == first_id:
            print('\n--- Sample of a <p> with multiple faculty images ---')
            print(p.get_text(' ', strip=True)[:800])
            break
 
# Print first 10 image tags' immediate parent tag name
print('\n--- First 10 images: parent tag names ---')
for img in imgs[:10]:
    print(f'  img parent tag: <{img.parent.name}>, grandparent: <{img.parent.parent.name if img.parent.parent else None}>')