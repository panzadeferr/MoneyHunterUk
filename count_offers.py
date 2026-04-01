#!/usr/bin/env python3
"""
Count offers in get_manual_offers() function
"""

import re

# Read scraper.py
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
# Look for everything from "def get_manual_offers()" to the next function definition
pattern = r'def get_manual_offers\(\) -> List\[Dict\]:.*?return \[(.*?)\]'
match = re.search(pattern, content, re.DOTALL)

if match:
    offers_text = match.group(1)
    # Count occurrences of "store": (each offer has one)
    offer_count = len(re.findall(r'"store"\s*:', offers_text))
    print(f"Total offers in get_manual_offers(): {offer_count}")
    
    # List all stores
    stores = re.findall(r'"store"\s*:\s*"([^"]+)"', offers_text)
    print(f"\nFirst 10 stores:")
    for i, store in enumerate(stores[:10]):
        print(f"  {i+1}. {store}")
    
    print(f"\nLast 10 stores:")
    for i, store in enumerate(stores[-10:]):
        print(f"  {offer_count-10+i+1}. {store}")
    
    # Check for specific stores from new_offers.json
    new_stores_to_check = ["First Direct", "Santander Edge", "Barclays", "Barclays Premier", 
                          "NatWest", "RBS", "Ulster Bank", "Co-operative Bank", "Metro Bank",
                          "HSBC", "Monzo", "Starling Bank", "Kroo", "Zing", "Trading212",
                          "InvestEngine", "Lightyear", "XTB", "Chip", "Raisin UK", "PensionBee",
                          "Nutmeg", "Circa5000", "EDF Energy", "Eon Next"]
    
    print(f"\nChecking for specific stores from new_offers.json:")
    found_count = 0
    for store in new_stores_to_check:
        if any(store in s for s in stores):
            print(f"  ✓ {store}")
            found_count += 1
        else:
            print(f"  ✗ {store} (not found)")
    
    print(f"\nFound {found_count}/{len(new_stores_to_check)} stores from new_offers.json")
    
    # Check if the file ends with incomplete offer
    if '"steps"' in content[-500:]:
        print("\n⚠️  WARNING: File appears to end with incomplete offer")
        print("Last 200 chars of file:")
        print(content[-200:])
else:
    print("Could not find get_manual_offers() function")