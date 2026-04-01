import json
import re

# Read the new offers JSON
with open('c:/Users/che23/Downloads/new_offers.json', 'r', encoding='utf-8') as f:
    new_offers = json.load(f)

print(f"Total new offers: {len(new_offers)}")

# Read the current scraper.py
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the get_manual_offers function ends (broken part)
# Look for the incomplete Eon Next offer
pattern = r'(\"store\": \"Eon Next\".*?steps)(\s*\n\s*\n# ============================================)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("Could not find the broken Eon Next offer")
    exit(1)

# Get the position of the broken part
broken_start = match.start(1)
broken_end = match.end(1)

# Find the start of the Eon Next offer
eon_start = content.rfind('{', 0, broken_start)

# Now we need to complete the function properly
# First, let's get everything before the broken part
before_broken = content[:eon_start]

# Now we need to add all the new offers
new_offers_str = ""
for i, offer in enumerate(new_offers):
    # Convert the offer to the same format as existing ones
    steps_str = json.dumps(offer['steps']).replace('"', "'")
    new_offer = f'        {{"store": "{offer["store"]}", "item": "{offer["item"]}", "deal_price": "{offer["deal_price"]}", "link": "{offer["link"]}", "original_price": "{offer["original_price"]}", "saving_percent": {offer["saving_percent"]}, "type": "{offer["type"]}", "category": "{offer["category"]}", "code": "{offer["code"]}", "expires": "{offer["expires"]}", "steps": {steps_str}, "badge": "{offer["badge"]}", "effort": "{offer["effort"]}"}},'
    new_offers_str += new_offer + '\n'

# Get everything after the broken part (starting from the next function)
after_broken = content[match.end(2):]

# Create the new content
new_content = before_broken + new_offers_str.rstrip() + '\n    ]\n\n' + after_broken

# Write back to file
with open('scraper.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully added {len(new_offers)} new offers to scraper.py")
print("Fixed the broken function by completing it properly")