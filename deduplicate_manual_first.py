#!/usr/bin/env python3
"""
Manual-First De-duplication System for Money Hunters UK

Purpose:
- Protect manual referrals by giving them priority over scraped deals
- Remove duplicates where scraped deals conflict with manual deals
- Keep manual deals intact, remove conflicting scraped deals
- Generate a clean, merged all_deals.json with manual-first approach
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

BASE_DIR = Path(__file__).resolve().parent
MANUAL_DEALS_PATH = BASE_DIR / "all_deals_clean.json"  # Manual deals backup
MEGALIST_PATH = BASE_DIR / "megalist.json"  # Scraped deals
OUTPUT_PATH = BASE_DIR / "all_deals.json"  # Final merged output

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_store_name(store: str) -> str:
    """Normalize store name for comparison."""
    if not store:
        return ""
    
    # Convert to lowercase
    store = store.lower().strip()
    
    # Remove common suffixes and prefixes
    store = re.sub(r'\s+(uk|uk\.|co\.uk|\.com|\.co\.uk|\.org|\.net)$', '', store)
    store = re.sub(r'^the\s+', '', store)
    
    # Remove punctuation and extra spaces
    store = re.sub(r'[^\w\s]', '', store)
    store = re.sub(r'\s+', ' ', store).strip()
    
    return store

def normalize_item_name(item: str) -> str:
    """Normalize item name for comparison."""
    if not item:
        return ""
    
    # Convert to lowercase
    item = item.lower().strip()
    
    # Remove common patterns
    item = re.sub(r'\s*[\(\[]\s*[^\)\]]*[\)\]]', '', item)  # Remove parentheses content
    item = re.sub(r'[^\w\s]', ' ', item)  # Replace punctuation with spaces
    item = re.sub(r'\s+', ' ', item).strip()
    
    # Remove common words
    common_words = ['offer', 'deal', 'bonus', 'reward', 'cashback', 'free', 'get', 'earn']
    words = item.split()
    filtered_words = [w for w in words if w not in common_words]
    item = ' '.join(filtered_words)
    
    return item[:100]  # Limit length

def extract_price_value(price_str: str) -> float:
    """Extract numeric price from price string."""
    if not price_str:
        return 0.0
    
    # Look for numbers in the string
    matches = re.findall(r'[\d,]+(?:\.\d+)?', price_str)
    if matches:
        try:
            # Take the first number found
            return float(matches[0].replace(',', ''))
        except ValueError:
            pass
    
    # Check for range like "10-100"
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', price_str)
    if range_match:
        try:
            return float(range_match.group(1))  # Use lower bound
        except ValueError:
            pass
    
    return 0.0

def is_similar_deal(deal1: Dict, deal2: Dict) -> bool:
    """
    Determine if two deals are similar enough to be considered duplicates.
    Manual-first approach: be conservative to protect manual deals.
    """
    # Normalize store names
    store1 = normalize_store_name(deal1.get('store', ''))
    store2 = normalize_store_name(deal2.get('store', ''))
    
    # Normalize item names
    item1 = normalize_item_name(deal1.get('item', ''))
    item2 = normalize_item_name(deal2.get('item', ''))
    
    # Extract prices
    price1 = extract_price_value(str(deal1.get('deal_price', '')))
    price2 = extract_price_value(str(deal2.get('deal_price', '')))
    
    # Rule 1: Exact store match with similar item
    if store1 and store2 and store1 == store2:
        # Check if items are similar (contain common words)
        item1_words = set(item1.split())
        item2_words = set(item2.split())
        common_words = item1_words.intersection(item2_words)
        
        # If they share at least 2 meaningful words, likely same deal
        if len(common_words) >= 2:
            return True
        
        # Check if prices are similar (within 20% or exact match)
        if price1 > 0 and price2 > 0:
            price_diff = abs(price1 - price2) / max(price1, price2)
            if price_diff < 0.2:  # Within 20%
                return True
    
    # Rule 2: Similar store names (fuzzy match)
    if store1 and store2 and store1 != store2:
        # Check for partial matches (e.g., "Lloyds Bank" vs "Lloyds")
        if store1 in store2 or store2 in store1:
            # And similar prices
            if price1 > 0 and price2 > 0 and abs(price1 - price2) < 50:
                return True
    
    # Rule 3: Check by link domain (if both have links)
    link1 = deal1.get('link', '')
    link2 = deal2.get('link', '')
    
    if link1 and link2:
        # Extract domain from links
        domain1 = re.search(r'https?://([^/]+)', link1)
        domain2 = re.search(r'https?://([^/]+)', link2)
        
        if domain1 and domain2:
            domain1 = domain1.group(1).lower()
            domain2 = domain2.group(1).lower()
            
            # Remove www. prefix for comparison
            domain1 = re.sub(r'^www\.', '', domain1)
            domain2 = re.sub(r'^www\.', '', domain2)
            
            if domain1 == domain2:
                # Same domain, check if store names are similar
                if store1 and store2 and (store1 in store2 or store2 in store1):
                    return True
    
    return False

def load_manual_deals() -> List[Dict]:
    """Load manual deals from backup file."""
    if not MANUAL_DEALS_PATH.exists():
        print(f"Warning: {MANUAL_DEALS_PATH} not found")
        return []
    
    try:
        with open(MANUAL_DEALS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        deals = data.get('deals', [])
        print(f"Loaded {len(deals)} manual deals from {MANUAL_DEALS_PATH}")
        return deals
    except Exception as e:
        print(f"Error loading manual deals: {e}")
        return []

def load_scraped_deals() -> List[Dict]:
    """Load scraped deals from megalist.json."""
    if not MEGALIST_PATH.exists():
        print(f"Warning: {MEGALIST_PATH} not found")
        return []
    
    try:
        with open(MEGALIST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        deals = data.get('deals', [])
        print(f"Loaded {len(deals)} scraped deals from {MEGALIST_PATH}")
        return deals
    except Exception as e:
        print(f"Error loading scraped deals: {e}")
        return []

def deduplicate_manual_first(manual_deals: List[Dict], scraped_deals: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    De-duplicate with manual-first approach.
    Returns: (clean_manual_deals, filtered_scraped_deals)
    """
    print("\nStarting manual-first de-duplication...")
    
    # Keep all manual deals as-is
    clean_manual = manual_deals.copy()
    
    # Filter scraped deals to remove conflicts with manual deals
    filtered_scraped = []
    conflicts_removed = 0
    
    for scraped_deal in scraped_deals:
        is_conflict = False
        
        # Check if this scraped deal conflicts with any manual deal
        for manual_deal in manual_deals:
            if is_similar_deal(scraped_deal, manual_deal):
                print(f"\nConflict detected:")
                print(f"  Manual: {manual_deal.get('store')} - {manual_deal.get('item')} ({manual_deal.get('deal_price')})")
                print(f"  Scraped: {scraped_deal.get('store')} - {scraped_deal.get('item')} ({scraped_deal.get('deal_price')})")
                print(f"  Action: Keeping manual, removing scraped")
                
                is_conflict = True
                conflicts_removed += 1
                break
        
        if not is_conflict:
            filtered_scraped.append(scraped_deal)
    
    print(f"\nDe-duplication complete:")
    print(f"  Manual deals kept: {len(clean_manual)}")
    print(f"  Scraped deals kept: {len(filtered_scraped)}")
    print(f"  Conflicts removed: {conflicts_removed}")
    
    return clean_manual, filtered_scraped

def merge_deals(manual_deals: List[Dict], scraped_deals: List[Dict]) -> Dict:
    """Merge manual and filtered scraped deals into final structure."""
    all_deals = manual_deals + scraped_deals
    
    # Update counts
    manual_count = len(manual_deals)
    scraped_count = len(scraped_deals)
    total_count = len(all_deals)
    
    # Create final structure
    output = {
        "last_updated": now_str(),
        "total_deals": total_count,
        "manual_count": manual_count,
        "supermarket_count": 0,  # Can be updated if needed
        "megalist_count": scraped_count,
        "cleaned_count": scraped_count,
        "sources": [
            "Manual",
            "Supermarket",
            "Reddit r/beermoneyuk",
            "Google News",
            "HotUKDeals",
            "MegaList"
        ],
        "stacking_rates": {
            "Tesco": 5.3,
            "Sainsbury's": 4.4,
            "Asda": 4.5,
            "Iceland": 5.0,
            "Morrisons": 4.0,
            "Waitrose": 3.5,
            "Aldi": 2.0,
            "Lidl": 2.0
        },
        "deals": all_deals
    }
    
    return output

def save_output(data: Dict) -> None:
    """Save merged data to all_deals.json."""
    try:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(data['deals'])} deals to {OUTPUT_PATH}")
        print(f"Manual: {data['manual_count']}, Scraped: {data['megalist_count']}")
    except Exception as e:
        print(f"Error saving output: {e}")

def main():
    """Main function to run manual-first de-duplication."""
    print("=" * 60)
    print("Manual-First De-duplication System")
    print("Protecting manual referrals from scraped duplicates")
    print("=" * 60)
    
    # Load deals
    manual_deals = load_manual_deals()
    scraped_deals = load_scraped_deals()
    
    if not manual_deals:
        print("Error: No manual deals found. Please ensure all_deals_clean.json exists.")
        return
    
    if not scraped_deals:
        print("Warning: No scraped deals found. Only manual deals will be used.")
    
    # Run de-duplication
    clean_manual, filtered_scraped = deduplicate_manual_first(manual_deals, scraped_deals)
    
    # Merge and save
    merged_data = merge_deals(clean_manual, filtered_scraped)
    save_output(merged_data)
    
    # Show summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total deals in final output: {len(merged_data['deals'])}")
    print(f"Manual deals protected: {len(clean_manual)}")
    print(f"Scraped deals added: {len(filtered_scraped)}")
    
    # Show sample of merged deals
    print("\nSample of merged deals (first 5):")
    for i, deal in enumerate(merged_data['deals'][:5]):
        source = "MANUAL" if i < len(clean_manual) else "SCRAPED"
        print(f"{i+1}. [{source}] {deal.get('store')} - {deal.get('item')} ({deal.get('deal_price')})")
    
    print("\n" + "=" * 60)
    print("De-duplication complete! Manual referrals are protected.")
    print("=" * 60)

if __name__ == "__main__":
    main()