#!/usr/bin/env python3
"""
Check which offers from new_offers.json are already in scraper.py
and add any missing ones.
"""

import json
import re

# Read the new_offers.json content from the user's uploaded file
# We'll use the first few offers as a sample
new_offers_data = [
    {
        "store": "First Direct",
        "item": "Switch Account — £175 Cash",
        "deal_price": "£175",
        "link": "https://www.firstdirect.com/banking/switch/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "category": "bank",
        "code": "",
        "expires": "2026-12-31",
        "steps": [
            "Open First Direct account",
            "Start CASS switch",
            "Pay in £1,000 within 30 days",
            "Wait for payout ~30 days"
        ],
        "badge": "🏦 BANK SWITCH",
        "effort": "12 min · CASS switch"
    },
    {
        "store": "Santander Edge",
        "item": "Switch Account — £220 Cash",
        "deal_price": "£220",
        "link": "https://www.santander.co.uk/personal/current-accounts",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "category": "bank",
        "code": "",
        "expires": "2026-12-31",
        "steps": [
            "Open Santander Edge account",
            "Start CASS switch",
            "Add 2 direct debits",
            "Pay in £1,500",
            "Wait for payout ~30 days"
        ],
        "badge": "🏦 BANK SWITCH",
        "effort": "12 min · CASS switch"
    },
    {
        "store": "Barclays",
        "item": "Switch Account — £200 Cash",
        "deal_price": "£200",
        "link": "https://www.barclays.co.uk/current-accounts/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "category": "bank",
        "code": "",
        "expires": "2026-05-28",
        "steps": [
            "Open Barclays Blue Rewards account",
            "Start CASS switch",
            "Meet eligibility requirements",
            "Wait for payout ~30 days"
        ],
        "badge": "🏦 BANK SWITCH",
        "effort": "12 min · CASS switch"
    }
]

def read_scraper():
    with open('scraper.py', 'r', encoding='utf-8') as f:
        return f.read()

def get_existing_offers(content):
    """Extract all store names from existing offers in scraper.py"""
    # Find the get_manual_offers function
    pattern = r'def get_manual_offers\(\) -> List\[Dict\]:.*?return \[(.*?)\n\s*\]'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return set()
    
    offers_text = match.group(1)
    
    # Extract all store names using regex
    store_pattern = r'"store"\s*:\s*"([^"]+)"'
    stores = re.findall(store_pattern, offers_text)
    
    return set(store.lower().strip() for store in stores)

def format_offer_for_insertion(offer):
    """Format an offer for insertion into the Python list"""
    # Convert steps list to JSON string
    steps_json = json.dumps(offer["steps"], ensure_ascii=False)
    
    # Build the dictionary string
    return f'        {{"store": "{offer["store"]}", "item": "{offer["item"]}", "deal_price": "{offer["deal_price"]}", "link": "{offer["link"]}", "original_price": "{offer["original_price"]}", "saving_percent": {offer["saving_percent"]}, "type": "{offer["type"]}", "category": "{offer["category"]}", "code": "{offer["code"]}", "expires": "{offer["expires"]}", "steps": {steps_json}, "badge": "{offer["badge"]}", "effort": "{offer["effort"]}"}},'

def main():
    print("Checking which offers are already in scraper.py...")
    
    # Read the current scraper.py
    content = read_scraper()
    
    # Get existing store names
    existing_stores = get_existing_offers(content)
    print(f"Found {len(existing_stores)} existing offers in scraper.py")
    
    # Check which new offers are already present
    missing_offers = []
    for offer in new_offers_data:
        store_name = offer["store"].lower().strip()
        if store_name not in existing_stores:
            missing_offers.append(offer)
            print(f"  Missing: {offer['store']}")
        else:
            print(f"  Already present: {offer['store']}")
    
    print(f"\nTotal missing offers: {len(missing_offers)}")
    
    if missing_offers:
        print("\nFormatted missing offers:")
        for offer in missing_offers:
            formatted = format_offer_for_insertion(offer)
            print(formatted)
        
        # Find where to insert (before the closing bracket)
        # Look for the closing bracket of the get_manual_offers list
        lines = content.split('\n')
        
        # Find the line with just ']' after the get_manual_offers function
        in_function = False
        for i, line in enumerate(lines):
            if 'def get_manual_offers() -> List[Dict]:' in line:
                in_function = True
                continue
            
            if in_function and line.strip() == ']':
                print(f"\nFound closing bracket at line {i+1}")
                print(f"Will insert new offers before line {i+1}")
                
                # Create the insertion text
                insertion_text = '\n'.join([format_offer_for_insertion(offer) for offer in missing_offers])
                
                # Insert the new offers
                lines.insert(i, insertion_text)
                
                # Write back to file
                with open('scraper.py', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"Successfully added {len(missing_offers)} new offers to scraper.py")
                break
    else:
        print("\nAll offers are already present in scraper.py!")

if __name__ == "__main__":
    main()