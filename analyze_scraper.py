import re

with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
pattern = r'def get_manual_offers\(\) -> List\[Dict\]:.*?(?=def |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    func_content = match.group(0)
    print(f'Function content length: {len(func_content)} chars')
    
    # Count offers
    offer_count = func_content.count('"store":')
    print(f'\nTotal offers in function: {offer_count}')
    
    # Find the closing bracket
    lines = func_content.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == ']':
            print(f'\nFound closing bracket at line {i+1} within function')
            print(f'Line: {line}')
            
            # Show context around closing bracket
            print('\nContext (5 lines before closing bracket):')
            for j in range(max(0, i-5), i):
                print(f'{j+1:4}: {lines[j].rstrip()}')
            
            print('\nContext (5 lines after closing bracket):')
            for j in range(i+1, min(i+6, len(lines))):
                print(f'{j+1:4}: {lines[j].rstrip()}')
            break
    
    # Extract all store names
    stores = re.findall(r'"store"\s*:\s*"([^"]+)"', func_content)
    print(f'\nFound {len(stores)} store names:')
    for i, store in enumerate(stores[:30]):
        print(f'  {i+1}. {store}')
    if len(stores) > 30:
        print(f'  ... and {len(stores)-30} more')
    
    # Check if we have all 60 new offers
    # The new offers should start after the original PensionBee offer
    # Let's find where the new offers start
    new_offer_start = func_content.find('"First Direct", "item": "Switch Account — £175 Cash"')
    if new_offer_start != -1:
        print(f'\nNew offers start at position {new_offer_start}')
        # Count offers after this point
        new_offers_section = func_content[new_offer_start:]
        new_offer_count = new_offers_section.count('"store":')
        print(f'Number of new offers found: {new_offer_count}')
else:
    print('Function not found')