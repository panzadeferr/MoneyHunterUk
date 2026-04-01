import re

with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
pattern = r'def get_manual_offers\(\) -> List\[Dict\]:.*?(?=def |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    func_content = match.group(0)
    # Find all store names
    stores = re.findall(r'"store"\s*:\s*"([^"]+)"', func_content)
    
    print(f'Total stores: {len(stores)}')
    print('\nLast 20 stores:')
    for i, store in enumerate(stores[-20:]):
        print(f'{len(stores)-20+i+1}. {store}')
    
    # Check which of the 60 new offers are missing
    # Based on the user's JSON, we need to check for specific stores
    expected_stores = [
        'First Direct', 'Santander Edge', 'Barclays', 'Barclays Premier', 'NatWest',
        'RBS', 'Ulster Bank', 'Co-operative Bank', 'Metro Bank', 'HSBC',
        'Monzo', 'Starling Bank', 'Kroo', 'Zing', 'Trading212',
        'InvestEngine', 'Lightyear', 'XTB', 'Chip', 'Raisin UK',
        'PensionBee', 'Nutmeg', 'Circa5000', 'EDF Energy', 'Eon Next',
        'Good Energy', 'So Energy', 'Sky', 'Virgin Media', 'TalkTalk',
        'Community Fibre', 'YouFibre', 'Hyperoptic', 'VOXI', 'Giffgaff',
        'O2', 'Three Mobile', 'Vodafone', 'Tesco Mobile', 'YouGov',
        'Cashback.co.uk', 'Custard', 'In-Poll', 'Measure (MSR)', 'Ribbon',
        'Gousto', 'Hello Fresh', 'Caffe Nero', 'Uber Eats', 'Deliveroo',
        'Airbnb', 'Expedia', 'Currensea', 'Remitly', 'WorldRemit',
        'Vitality', 'GoHenry', 'Rooster Money', 'Klarna', 'Clearpay'
    ]
    
    print('\nChecking for missing stores from the 60 new offers:')
    missing = []
    for store in expected_stores:
        found = False
        for s in stores:
            if store in s or s in store:
                found = True
                break
        if not found:
            missing.append(store)
    
    print(f'Missing {len(missing)} stores:')
    for store in missing:
        print(f'  - {store}')
    
    # Now let's find where the function ends
    lines = func_content.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == ']':
            print(f'\nFound closing bracket at line {i+1} within function')
            # Show the last complete offer
            print('\nLooking for last complete offer...')
            for j in range(i-1, max(0, i-20), -1):
                if '"store":' in lines[j]:
                    print(f'Last complete offer around line {j+1}:')
                    for k in range(max(0, j-3), min(len(lines), j+4)):
                        print(f'{k+1:4}: {lines[k].rstrip()}')
                    break
            break