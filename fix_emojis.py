#!/usr/bin/env python3
"""
Fix emoji characters in scraper.py
"""
import re

with open("scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace emoji print statements with text equivalents
replacements = [
    (r'print\("📡 Reddit random scraper disabled - using megalist"\)', 
     'print("Reddit random scraper disabled - using megalist")'),
    (r'print\("\n📡 Google News scraping DISABLED \(using MegaList instead\)..."\)', 
     'print("\nGoogle News scraping DISABLED (using MegaList instead)...")'),
    (r'print\("\n📡 Scraping HotUKDeals..."\)', 
     'print("\nScraping HotUKDeals...")'),
    (r'print\("\n📡 Scraping BeermoneyUK Megalist..."\)', 
     'print("\nScraping BeermoneyUK Megalist...")'),
    (r'print\("\n📡 Scraping Scrimpr..."\)', 
     'print("\nScraping Scrimpr...")'),
    (r'print\(f"✅ Total deals found: \{len\(all_deals\)\}"\)', 
     'print(f"Total deals found: {len(all_deals)}")'),
    (r'print\(f"📊 Data quality: \{len\(cleaned_scraped\)\}/\{len\(scraped\)\} deals passed validation"\)', 
     'print(f"Data quality: {len(cleaned_scraped)}/{len(scraped)} deals passed validation")'),
    (r'print\(f"💾 Saved to all_deals.json"\)', 
     'print(f"Saved to all_deals.json")'),
    (r'print\(f"📝 Log written to scrape_log.txt"\)', 
     'print(f"Log written to scrape_log.txt")'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Also fix any remaining emoji characters in print statements
emoji_pattern = r'print\(".*[🛒📦📡✅📊💾📝🏦📈⚡📺📱💰🍽️☕🍔✈️💸💼👨‍👩‍👧🛍️].*"\)'
# Instead of trying to match and replace complex patterns, just remove emojis from print statements
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'print(' in line and any(emoji in line for emoji in ['🛒', '📦', '📡', '✅', '📊', '💾', '📝', '🏦', '📈', '⚡', '📺', '📱', '💰', '🍽️', '☕', '🍔', '✈️', '💸', '💼', '👨‍👩‍👧', '🛍️']):
        # Remove emojis from print statements
        for emoji in ['🛒', '📦', '📡', '✅', '📊', '💾', '📝', '🏦', '📈', '⚡', '📺', '📱', '💰', '🍽️', '☕', '🍔', '✈️', '💸', '💼', '👨‍👩‍👧', '🛍️']:
            line = line.replace(emoji, '')
        lines[i] = line

content = '\n'.join(lines)

with open("scraper.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed emojis in scraper.py")