import re

# Read the scraper.py file
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
# Look for: def get_manual_offers() -> List[Dict]:
start = content.find('def get_manual_offers() -> List[Dict]:')
if start == -1:
    print("Could not find get_manual_offers function")
    exit()

# Find the return statement
return_start = content.find('return [', start)
if return_start == -1:
    print("Could not find return statement")
    exit()

# Find the matching closing bracket
bracket_count = 1
pos = return_start + len('return [')
while bracket_count > 0 and pos < len(content):
    if content[pos] == '[':
        bracket_count += 1
    elif content[pos] == ']':
        bracket_count -= 1
    pos += 1

if bracket_count == 0:
    list_end = pos - 1
    print(f"Found list from position {return_start} to {list_end}")
    
    # Get the list content
    list_content = content[return_start + len('return ['):list_end]
    
    # Count offers by counting occurrences of "store"
    store_count = list_content.count('"store"')
    print(f"Number of offers in list: {store_count}")
    
    # Find the last 500 characters of the list
    last_part = list_content[-500:] if len(list_content) > 500 else list_content
    print(f"\nLast part of the list:")
    print("-" * 80)
    print(last_part)
    print("-" * 80)
    
    # Find the position of the last offer
    # Look for the last complete dictionary
    dict_pattern = r'\{\s*"store".*?\}'
    dict_matches = list(re.finditer(dict_pattern, list_content, re.DOTALL))
    if dict_matches:
        last_match = dict_matches[-1]
        last_offer = last_match.group()
        print(f"\nLast offer (length: {len(last_offer)}):")
        print(last_offer[:200] + "..." if len(last_offer) > 200 else last_offer)
        
        # Find where this last offer ends in the original content
        last_offer_end_in_list = last_match.end()
        # Calculate position in original content
        last_offer_end_pos = return_start + len('return [') + last_offer_end_in_list
        print(f"\nLast offer ends at position: {last_offer_end_pos}")
        
        # Show what comes after the last offer
        after_offer = content[last_offer_end_pos:last_offer_end_pos + 100]
        print(f"\nAfter last offer (next 100 chars):")
        print(after_offer)
        
        # Find the closing bracket position
        closing_bracket_pos = content.find(']', last_offer_end_pos)
        if closing_bracket_pos != -1:
            print(f"\nClosing bracket at position: {closing_bracket_pos}")
            print(f"Text between last offer and closing bracket:")
            between_text = content[last_offer_end_pos:closing_bracket_pos]
            print(repr(between_text))
            
            # Create the exact search pattern
            # We need to find: last_offer + between_text + ]
            exact_pattern = re.escape(last_offer) + re.escape(between_text) + r'\]'
            print(f"\nExact pattern to search for (first 200 chars):")
            print(exact_pattern[:200] + "..." if len(exact_pattern) > 200 else exact_pattern)
else:
    print("Could not find matching closing bracket")