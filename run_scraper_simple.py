#!/usr/bin/env python3
"""
Simple script to run the scraper and capture output
"""
import subprocess
import sys
import os

# Change to the directory where scraper.py is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Running scraper.py...")
print("=" * 60)

# Run the scraper and capture output
result = subprocess.run(
    [sys.executable, "scraper.py"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

# Also run the JSON check
if result.returncode == 0 and os.path.exists("all_deals.json"):
    print("\n" + "=" * 60)
    print("Checking all_deals.json...")
    
    import json
    try:
        with open("all_deals.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Total deals: {data.get('total_deals', 'N/A')}")
        print(f"Manual count: {data.get('manual_count', 'N/A')}")
        print(f"Last updated: {data.get('last_updated', 'N/A')}")
    except Exception as e:
        print(f"Error reading JSON: {e}")