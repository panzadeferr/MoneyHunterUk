import json

# Read the original scraper.py
with open('scraper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Read the new offers JSON
with open('c:/Users/che23/Downloads/new_offers.json', 'r', encoding='utf-8') as f:
    new_offers = json.load(f)

# Find where the get_manual_offers function ends
function_start = -1
function_end = -1
for i, line in enumerate(lines):
    if 'def get_manual_offers() -> List[Dict]:' in line:
        function_start = i
    elif function_start != -1 and line.strip().startswith('def ') and i > function_start:
        function_end = i
        break

if function_end == -1:
    function_end = len(lines)

print(f'Function spans lines {function_start+1} to {function_end}')

# Find the incomplete Expedia offer (line 277 is 0-indexed 276)
# Actually, let's find the last complete line before the function ends
last_complete_line = -1
for i in range(function_end-1, function_start, -1):
    if lines[i].strip().endswith('},'):
        last_complete_line = i
        break

print(f'Last complete offer ends at line {last_complete_line+1}')

# Check if the Expedia offer is incomplete
# Line 277 (0-indexed 276) shows the Expedia offer is cut off
expedia_line = 276  # 0-indexed
if expedia_line < len(lines):
    print(f'Line {expedia_line+1}: {lines[expedia_line].rstrip()}')
    if 'Book a hotel (min' in lines[expedia_line] and not lines[expedia_line].strip().endswith('},'):
        print('Expedia offer is incomplete!')

# Now let's create the fixed content
# We'll rebuild from line 0 to the last complete offer, then add missing offers

# Find the Expedia offer from JSON
expedia_offer = None
missing_stores = ['Currensea', 'Remitly', 'WorldRemit', 'Vitality', 'GoHenry', 'Rooster Money', 'Klarna', 'Clearpay']
missing_offers = []

for offer in new_offers:
    if offer['store'] == 'Expedia':
        expedia_offer = offer
    elif offer['store'] in missing_stores:
        missing_offers.append(offer)

print(f'\nFound Expedia offer: {expedia_offer["store"] if expedia_offer else "Not found"}')
print(f'Found {len(missing_offers)} missing offers')

# Convert an offer to Python dictionary format
def offer_to_python(offer):
    # Format steps as a Python list
    steps_str = '["' + '", "'.join(offer['steps']) + '"]'
    
    # Handle special characters in badges
    badge = offer['badge'].replace('"', '\\"')
    
    return f'''        {{"store": "{offer['store']}", "item": "{offer['item']}", "deal_price": "{offer['deal_price']}", "link": "{offer['link']}", "original_price": "{offer['original_price']}", "saving_percent": {offer['saving_percent']}, "type": "{offer['type']}", "category": "{offer['category']}", "code": "{offer['code']}", "expires": "{offer['expires']}", "steps": {steps_str}, "badge": "{badge}", "effort": "{offer['effort']}"}},'''

# Create the new lines
new_lines = []

# Keep everything up to the last complete offer
# Find the line with the last complete offer (Airbnb)
for i in range(len(lines)):
    if i <= last_complete_line:
        new_lines.append(lines[i])
    else:
        break

# Now add the fixed Expedia offer
if expedia_offer:
    new_lines.append(offer_to_python(expedia_offer) + '\n')
else:
    # If we can't find it, use a placeholder
    new_lines.append('''        {"store": "Expedia", "item": "£25 off £200+ Hotel Booking", "deal_price": "£25", "link": "https://www.expedia.co.uk/", "original_price": "£200", "saving_percent": 12, "type": "referral", "category": "travel", "code": "", "expires": "2026-12-31", "steps": ["Sign up to Expedia via referral", "Book a hotel (min £200 spend)", "£25 discount applied"], "badge": "✈️ TRAVEL", "effort": "2 min · book hotel"},\n''')

# Add the missing offers
for offer in missing_offers:
    new_lines.append(offer_to_python(offer) + '\n')

# Add the closing bracket and return statement
new_lines.append('    ]\n')
new_lines.append('    return offers\n')

# Add the rest of the file (from after the function)
for i in range(function_end, len(lines)):
    new_lines.append(lines[i])

# Write the fixed file
with open('scraper_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f'\nCreated fixed file: scraper_fixed.py')
print(f'Original file length: {len(lines)} lines')
print(f'Fixed file length: {len(new_lines)} lines')

# Count offers in the fixed file
offer_count = 0
for line in new_lines:
    if '"store":' in line:
        offer_count += 1

print(f'Total offers in fixed file: {offer_count}')
print('Missing offers should now be added: Currensea, Remitly, WorldRemit, Vitality, GoHenry, Rooster Money, Klarna, Clearpay')