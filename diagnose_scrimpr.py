import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://scrimpr.co.uk/free-money-offers-uk/'
r = requests.get(url, headers=headers, timeout=15)
print('Status:', r.status_code)
soup = BeautifulSoup(r.content, 'html.parser')

# Look at H3 tags structure
h3_tags = soup.find_all('h3')
print(f'\nFound {len(h3_tags)} H3 tags')
for i, h3 in enumerate(h3_tags[:10]):  # Show first 10
    print(f'{i+1}. {h3.get_text(strip=True)[:100]}')

# Look for offer containers - check divs with specific classes
print('\nLooking for offer containers...')
# Common container classes for offers
container_classes = ['offer', 'deal', 'card', 'post', 'entry', 'content', 'item']
for class_name in container_classes:
    containers = soup.find_all('div', class_=lambda x: x and class_name in x.lower())
    if containers:
        print(f'Found {len(containers)} divs with class containing "{class_name}"')
        # Show first container structure
        if containers:
            print(f'First container text preview: {containers[0].get_text(strip=True)[:200]}')
            break

# Check for list items or structured content
print('\nChecking for list items...')
list_items = soup.find_all(['li', 'tr', 'td'])
print(f'Found {len(list_items)} list/table items')
if list_items:
    for i, item in enumerate(list_items[:5]):
        text = item.get_text(strip=True)
        if '£' in text:
            print(f'{i+1}. {text[:100]}')

# Check for paragraphs with pound signs
print('\nChecking paragraphs with £...')
paragraphs = soup.find_all('p')
pound_paragraphs = [p for p in paragraphs if '£' in p.get_text()]
print(f'Found {len(pound_paragraphs)} paragraphs with £')
for i, p in enumerate(pound_paragraphs[:5]):
    print(f'{i+1}. {p.get_text(strip=True)[:150]}')

# Save HTML for inspection
with open('scrimpr_page.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))