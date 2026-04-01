import json

# Load the JSON file
with open('all_deals.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract megalist deals
megalist_deals = [deal for deal in data['deals'] if deal.get('type') == 'megalist']

print(f"Megalist: {len(megalist_deals)} deals")
print("=" * 60)

# Show first 20 deals
for i, deal in enumerate(megalist_deals[:20]):
    print(f"{i+1:2}. {deal['store']:40} {deal['deal_price']:10} ({deal.get('category', 'N/A')})")
    print(f"    {deal['item'][:70]}...")
    print()

# Show summary
print(f"\nTotal megalist deals: {len(megalist_deals)}")
print(f"Total all deals: {data['total_deals']}")
print(f"Megalist count from metadata: {data['megalist_count']}")