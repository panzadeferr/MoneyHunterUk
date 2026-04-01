#!/usr/bin/env python3
"""
Find the exact end of the get_manual_offers() list
"""

with open('scraper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the get_manual_offers function
in_function = False
function_start = -1
bracket_count = 0
return_found = False

print("Searching for get_manual_offers() function...")

for i, line in enumerate(lines):
    if 'def get_manual_offers() -> List[Dict]:' in line:
        in_function = True
        function_start = i
        print(f"Found function at line {i+1}")
        continue
    
    if in_function and not return_found and 'return [' in line:
        return_found = True
        print(f"Found 'return [' at line {i+1}")
        # Start counting brackets from this line
        bracket_count = 1  # We have the opening bracket from 'return ['
        
        # Process from this line forward
        for j in range(i, len(lines)):
            line_text = lines[j]
            # Count brackets in this line
            bracket_count += line_text.count('[')
            bracket_count -= line_text.count(']')
            
            if bracket_count == 0:
                print(f"\nClosing bracket found at line {j+1}")
                print(f"Line {j+1}: {line_text.strip()}")
                
                # Show context around the closing bracket
                print(f"\nContext (lines {j-5} to {j+5}):")
                for k in range(max(0, j-5), min(len(lines), j+6)):
                    print(f"{k+1:4}: {lines[k].rstrip()}")
                
                # Count offers between return [ and this line
                offer_lines = lines[i:j+1]
                offer_text = ''.join(offer_lines)
                
                # Count occurrences of "store":
                store_count = offer_text.count('"store":')
                print(f"\nTotal offers found: {store_count}")
                
                # Show the last few offers
                print("\nLast 5 offers (by store name):")
                # Find all store names
                import re
                store_matches = re.findall(r'"store"\s*:\s*"([^"]+)"', offer_text)
                for idx, store in enumerate(store_matches[-5:]):
                    print(f"  {len(store_matches)-5+idx+1}. {store}")
                
                break
        break

if not return_found:
    print("Could not find 'return [' statement in function")