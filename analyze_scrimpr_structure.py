import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://scrimpr.co.uk/free-money-offers-uk/'
r = requests.get(url, headers=headers, timeout=15)
print('Status:', r.status_code)
soup = BeautifulSoup(r.content, 'html.parser')

# Find all H3 tags
h3_tags = soup.find_all('h3')
print(f'Found {len(h3_tags)} H3 tags')

# Let's examine the structure around H3 tags
for i, h3 in enumerate(h3_tags[:15]):  # Look at first 15
    print(f'\n--- Offer {i+1}: {h3.get_text(strip=True)[:50]} ---')
    
    # Get the parent container
    parent = h3.parent
    print(f'Parent tag: {parent.name}')
    if parent.get('class'):
        print(f'Parent classes: {parent.get("class")}')
    
    # Get all text in the parent container
    parent_text = parent.get_text(separator=' ', strip=True)
    if len(parent_text) > 300:
        print(f'Parent text preview: {parent_text[:300]}...')
    else:
        print(f'Parent text: {parent_text}')
    
    # Look for links in the parent
    links = parent.find_all('a', href=True)
    if links:
        print(f'Found {len(links)} links in parent')
        for link in links[:2]:  # Show first 2 links
            link_text = link.get_text(strip=True)
            if link_text:
                print(f'  Link text: {link_text[:50]}')
            print(f'  Link href: {link["href"][:100]}')
    
    # Look for pound amounts
    amounts = re.findall(r'£(\d+(?:\.\d{2})?)', parent_text)
    if amounts:
        print(f'Pound amounts: {amounts}')
    
    print('-' * 50)

# Now let's look for a specific pattern - offers with links and amounts
print('\n\n=== Looking for complete offers ===')
complete_offers = []
for h3 in h3_tags:
    parent = h3.parent
    parent_text = parent.get_text(separator=' ', strip=True)
    
    # Check if this looks like a real offer (has £ and a link)
    links = parent.find_all('a', href=True)
    amounts = re.findall(r'£(\d+(?:\.\d{2})?)', parent_text)
    
    if links and amounts:
        offer_name = h3.get_text(strip=True)
        # Get the first link that looks like an offer link (not navigation)
        offer_link = None
        for link in links:
            href = link['href']
            link_text = link.get_text(strip=True)
            # Skip navigation links
            if not href.startswith('#') and 'javascript' not in href:
                offer_link = href
                break
        
        if offer_link:
            complete_offers.append({
                'name': offer_name,
                'link': offer_link,
                'amounts': amounts,
                'text_preview': parent_text[:150]
            })

print(f'\nFound {len(complete_offers)} complete offers with links and amounts')
for i, offer in enumerate(complete_offers[:10]):
    print(f'\n{i+1}. {offer["name"]}')
    print(f'   Link: {offer["link"][:80]}')
    print(f'   Amounts: {offer["amounts"]}')
    print(f'   Preview: {offer["text_preview"]}')