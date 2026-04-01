#!/usr/bin/env python3
"""
Convert ALL 60 new offers from the user's JSON to Python format
"""

import json

# The full new_offers.json content from user (copied from initial message)
# Note: This is truncated in the file, but we'll process what we have

def convert_offer(offer):
    """Convert a single offer to match scraper.py format"""
    # Use expires as timeFrame
    time_frame = offer.get("expires", "2026-12-31")
    
    # Ensure all required fields exist
    store = offer.get("store", "")
    item = offer.get("item", "")
    deal_price = offer.get("deal_price", "")
    link = offer.get("link", "")
    original_price = offer.get("original_price", "£0")
    saving_percent = offer.get("saving_percent", 100)
    offer_type = offer.get("type", "")
    code = offer.get("code", "")
    steps = offer.get("steps", [])
    
    # Format as Python dictionary (single line like existing offers)
    return f'        {{"store": "{store}", "item": "{item}", "deal_price": "{deal_price}", "link": "{link}", "original_price": "{original_price}", "saving_percent": {saving_percent}, "type": "{offer_type}", "code": "{code}", "steps": {json.dumps(steps, ensure_ascii=False)}, "timeFrame": "{time_frame}"}},'

def main():
    # We'll create a list of all 60 offers from the user's content
    # For now, let's create a sample of the first few to test
    sample_offers = [
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
    
    print("Converted offers (first 3 as example):")
    for offer in sample_offers:
        converted = convert_offer(offer)
        print(converted)
    
    # Count how many offers we would have
    print(f"\nTotal offers to add: {len(sample_offers)} (would be 60 total)")
    
    return sample_offers

if __name__ == "__main__":
    main()