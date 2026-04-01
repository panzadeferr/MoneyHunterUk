import re

# Read the scraper.py file
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
pattern = r'def get_manual_offers\(\) -> List\[Dict\]:\s*"""All your original BeermoneyUK offers"""\s*return \[(.*?)\]\s*'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("Found get_manual_offers function")
    # Find the last offer before the closing bracket
    offers_text = match.group(1)
    
    # Split by lines to find the last offer
    lines = offers_text.strip().split('\n')
    
    # Find the last non-empty line before the closing bracket
    last_offer_line = None
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line and not line.startswith('#'):
            last_offer_line = line
            break
    
    print(f"Last offer line: {last_offer_line}")
    
    # Find the position of this line in the original content
    last_offer_pos = content.find(last_offer_line)
    print(f"Position of last offer line: {last_offer_pos}")
    
    # Find the position of the closing bracket after this line
    bracket_pos = content.find(']', last_offer_pos + len(last_offer_line))
    print(f"Position of closing bracket: {bracket_pos}")
    
    # Show context around the bracket
    print("\nContext around closing bracket:")
    print(content[bracket_pos-100:bracket_pos+10])
else:
    print("Could not find get_manual_offers function")