import re

# Read the scraper.py file
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
# Look for the pattern: def get_manual_offers() -> List[Dict]:
start_pos = content.find('def get_manual_offers() -> List[Dict]:')
if start_pos == -1:
    print("Could not find get_manual_offers function")
    exit()

# Find the return statement
return_pos = content.find('return [', start_pos)
if return_pos == -1:
    print("Could not find return statement")
    exit()

# Now find the matching closing bracket
bracket_count = 1
pos = return_pos + len('return [')
while bracket_count > 0 and pos < len(content):
    if content[pos] == '[':
        bracket_count += 1
    elif content[pos] == ']':
        bracket_count -= 1
    pos += 1

if bracket_count == 0:
    print(f"Found closing bracket at position: {pos-1}")
    print(f"Context around closing bracket:")
    print(content[pos-100:pos+10])
    
    # Show the last few lines before the bracket
    lines_before = content[:pos].split('\n')[-5:]
    print("\nLast 5 lines before closing bracket:")
    for line in lines_before:
        print(line)
else:
    print("Could not find matching closing bracket")