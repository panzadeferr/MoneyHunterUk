import json

d = json.load(open('all_deals.json'))
print('Total deals:', d['total_deals'])
print('Scrimpr deals:', d['scrimpr_count'])

# Count deals by type
types = {}
for deal in d['deals']:
    t = deal.get('type', 'unknown')
    types[t] = types.get(t, 0) + 1

print('\nDeal types:')
for t, c in sorted(types.items()):
    print(f'  {t}: {c}')

# Show some Scrimpr deals
print('\nSample Scrimpr deals:')
scrimpr_deals = [deal for deal in d['deals'] if deal.get('type') == 'scrimpr']
for i, deal in enumerate(scrimpr_deals[:10]):
    print(f'{i+1}. {deal["store"]}: {deal["deal_price"]} - {deal["item"][:60]}...')

# Check what categories Scrimpr deals have
print('\nScrimpr deal categories:')
categories = {}
for deal in scrimpr_deals:
    cat = deal.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f'  {cat}: {count}')