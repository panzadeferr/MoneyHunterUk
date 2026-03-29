import json

with open('all_deals.json', 'r') as f:
    data = json.load(f)

print(f"Total deals: {data['total_deals']}")
print(f"Reddit deals: {data['reddit_count']}")
print(f"Unique scraped: {data['unique_scraped_count']}")
print()

print("Sample of cleaned store names:")
for i, deal in enumerate(data['deals'][:5]):
    print(f"  {i+1}. {deal['store'][:50]}")
print()

print("Categories in first 10 deals:")
categories = set()
for deal in data['deals'][:10]:
    categories.add(deal.get('category', 'none'))
print(f"  {list(categories)}")
print()

print("Data structure check - first deal keys:")
if data['deals']:
    first_deal = data['deals'][0]
    print(f"  Keys: {list(first_deal.keys())}")
    print(f"  Has category: {'category' in first_deal}")
    print(f"  Has type: {'type' in first_deal}")
    print(f"  Store cleaned: {first_deal['store']}")