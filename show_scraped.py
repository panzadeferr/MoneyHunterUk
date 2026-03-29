import json

with open('all_deals.json', 'r') as f:
    data = json.load(f)

scraped_reddit = [deal for deal in data['deals'] if deal.get('type') == 'scraped_reddit']
print(f'Found {len(scraped_reddit)} scraped_reddit entries')
print('=' * 80)
for i, deal in enumerate(scraped_reddit[:5], 1):
    print(f'Entry {i}:')
    print(f'  Store: {deal["store"][:50]}...')
    print(f'  Item: {deal["item"][:50]}...')
    print(f'  Deal Price: {deal["deal_price"]}')
    print(f'  Reddit Score: {deal.get("reddit_score", "N/A")}')
    print(f'  Link: {deal["link"][:80]}...')
    print()