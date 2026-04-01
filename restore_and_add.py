import json
import re

# Read the backup file
with open('scraper_backup.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Read backup file: {len(content)} characters")

# Find the get_manual_offers function
start = content.find('def get_manual_offers() -> List[Dict]:')
if start == -1:
    print("ERROR: Could not find get_manual_offers function in backup")
    exit(1)

# Find the return statement
return_start = content.find('return [', start)
if return_start == -1:
    print("ERROR: Could not find return statement in backup")
    exit(1)

# Find the closing bracket of the return statement
bracket_count = 1
pos = return_start + len('return [')

while bracket_count > 0 and pos < len(content):
    if content[pos] == '[':
        bracket_count += 1
    elif content[pos] == ']':
        bracket_count -= 1
    pos += 1

if bracket_count != 0:
    print("ERROR: Could not find matching closing bracket in backup")
    exit(1)

closing_bracket_pos = pos - 1

print(f"Found closing bracket at position: {closing_bracket_pos}")

# Get everything before and after the closing bracket
before_bracket = content[:closing_bracket_pos]
after_bracket = content[closing_bracket_pos:]

# Check what the last offer looks like
last_offer_start = before_bracket.rfind('{')
last_offer_end = before_bracket.rfind('}')

if last_offer_start != -1 and last_offer_end != -1 and last_offer_end > last_offer_start:
    last_offer = before_bracket[last_offer_start:last_offer_end+1]
    print(f"\nLast offer in backup (first 200 chars):")
    print(last_offer[:200] + "..." if len(last_offer) > 200 else last_offer)
    
    # Check format
    if '"timeFrame"' in last_offer:
        print("Format: Has 'timeFrame' field (original format)")
        format_type = "original"
    elif '"expires"' in last_offer:
        print("Format: Has 'expires' field (new format)")
        format_type = "new"
    else:
        print("Format: Unknown")
        format_type = "original"
else:
    print("Could not find last offer")
    format_type = "original"

# Now let's create the 60 new offers in the correct format
# Based on the backup, it uses the original format with "timeFrame" not "expires"
# and doesn't have "category", "badge", "effort" fields

# Parse the new_offers.json from the user's message
# I'll create a Python representation of the first few offers to test
new_offers_json = [
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
  }
]

# Convert new format to original format
def convert_to_original_format(offer):
    """Convert new format offer to original format"""
    # Create a copy
    original = offer.copy()
    
    # Rename expires to timeFrame
    if "expires" in original:
        original["timeFrame"] = f"Until {original['expires']}"
        del original["expires"]
    
    # Remove fields not in original format
    fields_to_remove = ["category", "badge", "effort"]
    for field in fields_to_remove:
        if field in original:
            del original[field]
    
    return original

# Convert all new offers
converted_offers = []
for offer in new_offers_json:
    converted = convert_to_original_format(offer)
    converted_offers.append(converted)

print(f"\nConverted {len(converted_offers)} offers to original format")

# Now create the Python code for these offers
offer_strings = []
for offer in converted_offers:
    # Convert to Python dict string
    # Format steps as a list
    steps_str = json.dumps(offer["steps"]).replace('"', "'")
    
    offer_str = f'        {{"store": "{offer["store"]}", "item": "{offer["item"]}", "deal_price": "{offer["deal_price"]}", "link": "{offer["link"]}", "original_price": "{offer["original_price"]}", "saving_percent": {offer["saving_percent"]}, "type": "{offer["type"]}", "code": "{offer["code"]}", "steps": {steps_str}, "timeFrame": "{offer.get("timeFrame", "Varies")}"}}'
    offer_strings.append(offer_str)

# Join all offers
all_offers_text = ',\n'.join(offer_strings)

print(f"\nGenerated {len(offer_strings)} offer strings")
print(f"First offer string:\n{offer_strings[0]}")

# Now we need to insert these offers before the closing bracket
# But actually, we should restore the backup first, then add ALL 60 offers
# For now, let's just restore the backup

# Write the backup content to scraper.py
with open('scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Restored scraper.py from backup")

# Now we need to actually add all 60 offers
# Let me create a separate script to parse the full new_offers.json
# and add all 60 offers properly