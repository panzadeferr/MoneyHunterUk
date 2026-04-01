import re

with open('scraper.py', 'r', encoding='utf-8') as f:
    # Read last 5000 characters to find the end of get_manual_offers
    f.seek(0, 2)
    file_size = f.tell()
    f.seek(max(0, file_size - 5000))
    end_content = f.read()

# Look for the get_manual_offers function in the end content
# We need to find where it ends
lines = end_content.split('\n')

# Look for patterns that indicate the end of the list
for i, line in enumerate(lines):
    if ']' in line and 'return [' not in line:
        # Check if this looks like the closing bracket of get_manual_offers
        # by looking at context
        context = '\n'.join(lines[max(0, i-5):min(len(lines), i+5)])
        if 'get_manual_offers' in context or 'def ' in context:
            print(f"Possible closing bracket at line position {i}:")
            print(f"Line: {line}")
            print(f"Context:\n{context}")
            print("-" * 80)

# Also look for the actual end of the function
print("\nSearching for function end...")
for i, line in enumerate(lines):
    if 'def ' in line and i > 10:  # Skip if it's near the beginning of our snippet
        print(f"Found function definition at line {i}: {line.strip()}")
        # Show what comes before it
        print("Previous 3 lines:")
        for j in range(max(0, i-3), i):
            print(f"  {lines[j]}")
        print()

# Let's also check if we can find where the list ends by counting brackets
print("\nTrying to find list end by bracket matching...")
content = open('scraper.py', 'r', encoding='utf-8').read()
# Find the get_manual_offers function
match = re.search(r'def get_manual_offers\(\) -> List\[Dict\]:.*?return \[', content, re.DOTALL)
if match:
    start_pos = match.end()
    print(f"Found 'return [' at position {start_pos}")
    
    # Now find the matching closing bracket
    bracket_count = 1
    pos = start_pos
    while pos < len(content) and bracket_count > 0:
        if content[pos] == '[':
            bracket_count += 1
        elif content[pos] == ']':
            bracket_count -= 1
        pos += 1
    
    if bracket_count == 0:
        end_pos = pos - 1
        print(f"Found matching ']' at position {end_pos}")
        
        # Extract the list content
        list_content = content[start_pos:end_pos]
        lines_in_list = list_content.count('\n')
        print(f"List spans {lines_in_list} lines")
        
        # Show the last 100 characters before the closing bracket
        preview_start = max(0, end_pos - 200)
        preview = content[preview_start:end_pos+1]
        print(f"\nLast 200 characters before closing bracket:")
        print(preview)
    else:
        print("Could not find matching closing bracket")