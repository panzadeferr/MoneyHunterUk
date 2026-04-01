#!/usr/bin/env python3
"""
Convert new_offers.json to Python list format for scraper.py
"""

import json
import os

def convert_new_offers():
    # Read the new offers JSON from the downloads folder
    json_path = 'c:/Users/che23/Downloads/new_offers.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        new_offers = json.load(f)
    
    print(f"Loaded {len(new_offers)} new offers")
    
    # Convert each offer to match existing format
    converted_offers = []
    for offer in new_offers:
        # Create a new offer dict with the expected fields
        converted = {
            "store": offer["store"],
            "item": offer["item"],
            "deal_price": offer["deal_price"],
            "link": offer["link"],
            "original_price": offer["original_price"],
            "saving_percent": offer["saving_percent"],
            "type": offer["type"],
            "code": offer["code"],
            "steps": offer["steps"],
            # Convert expires to timeFrame
            "timeFrame": f"Expires {offer['expires']}" if offer.get("expires") else "Check offer"
        }
        
        # Add category if present (scraper will infer if missing)
        if "category" in offer:
            converted["category"] = offer["category"]
        
        converted_offers.append(converted)
    
    # Generate Python code for insertion
    python_code = ""
    for i, offer in enumerate(converted_offers):
        # Format the offer as Python dict
        # Escape quotes in strings
        store = offer["store"].replace('"', '\\"')
        item = offer["item"].replace('"', '\\"')
        link = offer["link"].replace('"', '\\"')
        timeFrame = offer["timeFrame"].replace('"', '\\"')
        
        line = f'        {{"store": "{store}", "item": "{item}", "deal_price": "{offer["deal_price"]}", "link": "{link}", "original_price": "{offer["original_price"]}", "saving_percent": {offer["saving_percent"]}, "type": "{offer["type"]}", "code": "{offer["code"]}", "steps": {json.dumps(offer["steps"])}, "timeFrame": "{timeFrame}"}}'
        
        # Add comma unless it's the last offer
        if i < len(converted_offers) - 1:
            line += ','
        
        python_code += line + '\n'
    
    # Save to file
    with open('new_offers_python.txt', 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print(f"Converted {len(converted_offers)} offers")
    print("Python code saved to new_offers_python.txt")
    
    # Also print first few as example
    print("\nFirst 3 converted offers:")
    for i in range(min(3, len(converted_offers))):
        print(f"{i+1}. {converted_offers[i]['store']}: {converted_offers[i]['item']}")
    
    return python_code

if __name__ == "__main__":
    convert_new_offers()