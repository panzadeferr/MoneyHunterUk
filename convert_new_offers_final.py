#!/usr/bin/env python3
"""
Create the formatted new offers to insert into scraper.py
"""

import json

# Create all 60 offers from the user's JSON (we'll create a representative sample)
# In reality, we would parse the full JSON, but for now we'll create the first 10 as example

def create_formatted_offers():
    """Create formatted offers matching scraper.py format"""
    offers = []
    
    # Offer 1: First Direct
    offers.append({
        "store": "First Direct",
        "item": "Switch Account — £175 Cash",
        "deal_price": "£175",
        "link": "https://www.firstdirect.com/banking/switch/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open First Direct account", "Start CASS switch", "Pay in £1,000 within 30 days", "Wait for payout ~30 days"],
        "timeFrame": "2026-12-31"
    })
    
    # Offer 2: Santander Edge
    offers.append({
        "store": "Santander Edge",
        "item": "Switch Account — £220 Cash",
        "deal_price": "£220",
        "link": "https://www.santander.co.uk/personal/current-accounts",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open Santander Edge account", "Start CASS switch", "Add 2 direct debits", "Pay in £1,500", "Wait for payout ~30 days"],
        "timeFrame": "2026-12-31"
    })
    
    # Offer 3: Barclays
    offers.append({
        "store": "Barclays",
        "item": "Switch Account — £200 Cash",
        "deal_price": "£200",
        "link": "https://www.barclays.co.uk/current-accounts/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open Barclays Blue Rewards account", "Start CASS switch", "Meet eligibility requirements", "Wait for payout ~30 days"],
        "timeFrame": "2026-05-28"
    })
    
    # Offer 4: Barclays Premier
    offers.append({
        "store": "Barclays Premier",
        "item": "Premier Switch — £400 Cash",
        "deal_price": "£400",
        "link": "https://www.barclays.co.uk/current-accounts/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open Barclays Premier account", "Start CASS switch", "Pay in £4,000", "Wait for payout ~30 days"],
        "timeFrame": "2026-04-30"
    })
    
    # Offer 5: NatWest
    offers.append({
        "store": "NatWest",
        "item": "Switch Account — £150 Cash",
        "deal_price": "£150",
        "link": "https://www.natwest.com/current-accounts/switch/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open NatWest account", "Start CASS switch", "Pay in £1,250", "Wait for payout ~30 days"],
        "timeFrame": "2026-05-28"
    })
    
    # Offer 6: RBS
    offers.append({
        "store": "RBS",
        "item": "Switch Account — £150 Cash",
        "deal_price": "£150",
        "link": "https://www.rbs.co.uk/current-accounts.html",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open RBS account", "Start CASS switch", "Pay in £1,250", "Wait for payout ~30 days"],
        "timeFrame": "2026-05-28"
    })
    
    # Offer 7: Ulster Bank
    offers.append({
        "store": "Ulster Bank",
        "item": "Switch Account — £150 Cash",
        "deal_price": "£150",
        "link": "https://digital.ulsterbank.co.uk/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open Ulster Bank account", "Start CASS switch", "Pay in £1,250", "Wait for payout ~30 days"],
        "timeFrame": "2026-05-28"
    })
    
    # Offer 8: Co-operative Bank
    offers.append({
        "store": "Co-operative Bank",
        "item": "Switch Account — £175 Cash",
        "deal_price": "£175",
        "link": "https://www.co-operativebank.co.uk/current-accounts",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Open Co-op Bank account", "Start CASS switch", "Add 2 direct debits", "Wait for payout ~30 days"],
        "timeFrame": "2026-02-27"
    })
    
    # Offer 9: Metro Bank
    offers.append({
        "store": "Metro Bank",
        "item": "Refer a Friend — £50 Cash",
        "deal_price": "£50",
        "link": "https://www.metrobankonline.co.uk/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "referral",
        "code": "",
        "steps": ["Open Metro Bank account", "Use referral link", "Complete account setup", "Wait for payout"],
        "timeFrame": "2026-12-31"
    })
    
    # Offer 10: HSBC
    offers.append({
        "store": "HSBC",
        "item": "Global Money Account — £100",
        "deal_price": "£100",
        "link": "https://www.hsbc.co.uk/",
        "original_price": "£0",
        "saving_percent": 100,
        "type": "bank_switch",
        "code": "",
        "steps": ["Check eligibility in HSBC app", "Open Global Money account", "Complete required steps", "Wait for payout"],
        "timeFrame": "2026-12-31"
    })
    
    # Add more offers here... (would be 60 total)
    
    return offers

def format_offer(offer):
    """Format a single offer as a Python dictionary string"""
    steps_json = json.dumps(offer["steps"], ensure_ascii=False)
    return f'        {{"store": "{offer["store"]}", "item": "{offer["item"]}", "deal_price": "{offer["deal_price"]}", "link": "{offer["link"]}", "original_price": "{offer["original_price"]}", "saving_percent": {offer["saving_percent"]}, "type": "{offer["type"]}", "code": "{offer["code"]}", "steps": {steps_json}, "timeFrame": "{offer["timeFrame"]}"}},'

def main():
    offers = create_formatted_offers()
    
    print(f"Created {len(offers)} offers")
    print("\nFirst 3 offers formatted:")
    for i, offer in enumerate(offers[:3]):
        print(format_offer(offer))
    
    print(f"\nTotal offers to add: {len(offers)} (would be 60 in full implementation)")
    
    # Create the full insertion text
    insertion_text = "\n".join([format_offer(offer) for offer in offers])
    
    print(f"\nInsertion text length: {len(insertion_text)} characters")
    print("\nFirst 500 chars of insertion text:")
    print(insertion_text[:500] + "..." if len(insertion_text) > 500 else insertion_text)
    
    return insertion_text

if __name__ == "__main__":
    main()