import os

print("Testing scraper.py update...")
print(f"Current directory: {os.getcwd()}")
print(f"scraper.py exists: {os.path.exists('scraper.py')}")
print(f"scraper_fixed.py exists: {os.path.exists('scraper_fixed.py')}")

if os.path.exists('scraper.py'):
    with open('scraper.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    offer_count = content.count('"store":')
    print(f"\nTotal offers in scraper.py: {offer_count}")
    
    # Check for some key stores
    key_stores = ['First Direct', 'Expedia', 'Currensea', 'Clearpay']
    print("\nChecking key stores:")
    for store in key_stores:
        if store in content:
            print(f"  ✓ {store} - Found")
        else:
            print(f"  ✗ {store} - Missing")
    
    # Check if function ends properly
    if 'return offers' in content:
        print("\n✓ Function ends with 'return offers'")
    else:
        print("\n✗ Function doesn't end properly")
    
    # Check last few lines of get_manual_offers function
    import re
    pattern = r'def get_manual_offers\(\) -> List\[Dict\]:.*?(?=def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        func_content = match.group(0)
        lines = func_content.split('\n')
        print(f"\nLast 5 lines of get_manual_offers():")
        for line in lines[-5:]:
            print(f"  {line.rstrip()}")
else:
    print("ERROR: scraper.py not found!")