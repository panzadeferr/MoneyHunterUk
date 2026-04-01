# Simple script to find the exact location
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
start = content.find('def get_manual_offers() -> List[Dict]:')
if start == -1:
    print("Function not found")
    exit()

# Find the return statement
return_start = content.find('return [', start)
if return_start == -1:
    print("Return statement not found")
    exit()

# Now find the matching closing bracket
bracket_count = 1
pos = return_start + len('return [')

while bracket_count > 0 and pos < len(content):
    if content[pos] == '[':
        bracket_count += 1
    elif content[pos] == ']':
        bracket_count -= 1
    pos += 1

if bracket_count == 0:
    closing_pos = pos - 1
    print(f"Closing bracket found at position: {closing_pos}")
    
    # Show the last 300 characters before the closing bracket
    print("\nLast 300 characters before closing bracket:")
    last_part = content[closing_pos-300:closing_pos]
    print(last_part)
    
    # Find the last complete offer before the bracket
    # Look for the last closing brace }
    last_brace = last_part.rfind('}')
    if last_brace != -1:
        # Find the matching opening brace
        brace_count = 1
        brace_pos = last_brace - 1
        while brace_count > 0 and brace_pos >= 0:
            if last_part[brace_pos] == '}':
                brace_count += 1
            elif last_part[brace_pos] == '{':
                brace_count -= 1
            brace_pos -= 1
        
        if brace_count == 0:
            offer_start = brace_pos + 1
            last_offer = last_part[offer_start:last_brace+1]
            print(f"\nLast offer found (first 200 chars):")
            print(last_offer[:200] + "..." if len(last_offer) > 200 else last_offer)
            
            # Extract store name
            import re
            store_match = re.search(r'"store"\s*:\s*"([^"]+)"', last_offer)
            if store_match:
                print(f"\nStore name in last offer: {store_match.group(1)}")