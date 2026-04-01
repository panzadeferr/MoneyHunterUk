import re

# Read the scraper.py file
with open('scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_manual_offers function
pattern = r'def get_manual_offers\(\) -> List\[Dict\]:\s*""".*?"""\s*return \[(.*?)\n\s*\]'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("Found get_manual_offers function")
    # Find the line numbers
    lines = content.split('\n')
    in_function = False
    bracket_count = 0
    start_line = -1
    end_line = -1
    
    for i, line in enumerate(lines):
        if 'def get_manual_offers() -> List[Dict]:' in line:
            in_function = True
            start_line = i
            print(f"Function starts at line {i+1}: {line}")
        
        if in_function:
            if 'return [' in line:
                print(f"Return statement at line {i+1}: {line}")
            
            # Count brackets to find the end
            bracket_count += line.count('[')
            bracket_count -= line.count(']')
            
            if bracket_count == -1:  # We found the closing bracket of the return list
                end_line = i
                print(f"Closing bracket found at line {i+1}: {line}")
                print(f"Previous line ({i}): {lines[i-1]}")
                print(f"Next line ({i+1}): {lines[i+1] if i+1 < len(lines) else 'END OF FILE'}")
                break
    
    if start_line != -1 and end_line != -1:
        print(f"\nFunction spans lines {start_line+1} to {end_line+1}")
        print(f"\nLast few lines of the list:")
        for j in range(max(start_line, end_line-5), end_line+2):
            print(f"{j+1}: {lines[j]}")
else:
    print("Could not find get_manual_offers function")