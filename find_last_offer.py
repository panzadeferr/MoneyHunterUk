import re

# Read the scraper.py file
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
# Look for everything from "def get_manual_offers" to the closing bracket of the return statement
pattern = r'def get_manual_offers\(\) -> List\[Dict\]:.*?return \[(.*?)\]\s*(?=\n\s*#|\n\s*def|\n\s*""")'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("Found get_manual_offers function")
    offers_text = match.group(1)
    
    # Find all individual offers
    offers = re.findall(r'\{[^}]*"(?:store|item)"[^}]*\}', offers_text)
    print(f"Total offers found: {len(offers)}")
    
    if offers:
        # Get the last offer
        last_offer = offers[-1]
        print(f"\nLast offer (first 200 chars):")
        print(last_offer[:200] + "..." if len(last_offer) > 200 else last_offer)
        
        # Find the position of this last offer in the original content
        last_offer_pos = content.find(last_offer)
        print(f"\nPosition of last offer: {last_offer_pos}")
        
        # Find the closing bracket after this offer
        bracket_pos = content.find(']', last_offer_pos + len(last_offer))
        print(f"Position of closing bracket: {bracket_pos}")
        
        # Show more context
        print(f"\nContext around closing bracket (50 chars before and after):")
        start = max(0, bracket_pos - 50)
        end = min(len(content), bracket_pos + 10)
        context = content[start:end]
        print(context.replace('\n', '\\n'))
        
        # Show what comes after the bracket
        print(f"\nWhat comes after the bracket (next 50 chars):")
        after_bracket = content[bracket_pos:bracket_pos + 50]
        print(after_bracket.replace('\n', '\\n'))
else:
    print("Could not find get_manual_offers function")