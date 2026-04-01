#!/usr/bin/env python3
"""
Find the exact end of the manual offers list
"""

with open('scraper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look for the PensionBee offer (the last offer in the current list)
for i, line in enumerate(lines):
    if 'PensionBee' in line and 'Sign Up → £50 in Pension' in line:
        print(f'Found PensionBee offer at line {i+1}')
        print(f'Line content: {line.rstrip()[:100]}...')
        
        # Now find the closing bracket after this offer
        # Look for a line with just ']' (closing bracket of the list)
        for j in range(i+1, min(i+20, len(lines))):
            if lines[j].strip() == ']':
                print(f'\nFound closing bracket at line {j+1}')
                
                # The insertion point is right before the closing bracket
                # We need to insert after the last offer (PensionBee)
                # Find which line has the closing }, for PensionBee
                for k in range(i, j):
                    if '},' in lines[k] or (k < j-1 and '}' in lines[k] and '},' not in lines[k+1]):
                        print(f'\nLast offer ends at line {k+1}')
                        print(f'Insert new offers AFTER line {k+1}')
                        
                        print('\nContext around insertion point:')
                        for m in range(max(0, k-2), min(len(lines), k+4)):
                            prefix = '>>>' if m == k else '   '
                            print(f'{prefix} {m+1:4}: {lines[m].rstrip()}')
                        
                        # Also show what comes after
                        print('\nWhat comes after (next 5 lines):')
                        for m in range(k+1, min(len(lines), k+6)):
                            print(f'    {m+1:4}: {lines[m].rstrip()}')
                        
                        return_line = k
                        break
                break
        break

# If we get here, we didn't find it
print("Could not find PensionBee offer or closing bracket")