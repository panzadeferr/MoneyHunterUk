import scraper

deals = scraper.get_supermarket_deals()
print(f'Total supermarket deals: {len(deals)}')

# Count occurrences of each supermarket
from collections import Counter
supermarkets = [deal["store"] for deal in deals]
counts = Counter(supermarkets)

print('\nSupermarket counts:')
for store, count in counts.items():
    print(f'  {store}: {count} times')

print('\nAll entries:')
for i, deal in enumerate(deals):
    print(f'{i+1}. {deal["store"]}: {deal["item"]} - {deal["deal_price"]}')
    
    # Check for "Up to X% off" or "Exclusive prices" in item field
    item = deal["item"]
    if "Up to" in item and "% off" in item:
        print(f'   WARNING: Contains "Up to X% off" in item field')
    if "Exclusive prices" in item:
        print(f'   WARNING: Contains "Exclusive prices" in item field')