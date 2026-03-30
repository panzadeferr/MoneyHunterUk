"""
MegaList Scraper with AI Guide Generation
- Parses markdown tables from MegaList
- Deep crawls sub-list links with loop protection
- Generates AI step-by-step guides
- Cleans up ghost offers
"""

import json
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin

# ============================================
# CORE PARSING FUNCTIONS
# ============================================

def extract_direct_url(text: str) -> str:
    """
    Extract destination URL from markdown links, bypassing Reddit redirects.
    Priority: Direct URLs > Reddit post links > No URL
    """
    # Find all markdown links [text](url)
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
    
    for link_text, url in markdown_links:
        # Skip Reddit redirects
        if 'out.reddit.com' in url or 'reddit.com/r/' in url:
            continue
        
        # Check if it's a direct URL (not Reddit)
        if re.match(r'https?://(?!.*reddit\.com)[\w\-\.]+\.[a-z]{2,}', url):
            return url
    
    # If no markdown links, look for raw URLs
    raw_urls = re.findall(r'https?://[^\s\)]+', text)
    for url in raw_urls:
        if 'out.reddit.com' in url or 'reddit.com/r/' in url:
            continue
        if re.match(r'https?://(?!.*reddit\.com)[\w\-\.]+\.[a-z]{2,}', url):
            return url
    
    # Last resort: return first Reddit link (but mark it)
    if markdown_links:
        return markdown_links[0][1]
    
    return ""

def parse_markdown_table(text: str) -> List[Dict]:
    """
    Parse markdown tables in format:
    | Offer Name | Reward | Requirements/Link |
    |------------|--------|-------------------|
    | Lloyds Bank | £250 | Sign up and switch |
    """
    offers = []
    
    # Find all markdown tables
    table_pattern = r'\|([^\n]+)\|\s*\n\|[-:]+\|\s*\n((?:\|[^\n]+\|\s*\n?)+)'
    tables = re.findall(table_pattern, text, re.MULTILINE)
    
    for header_row, table_body in tables:
        # Parse header to understand column order
        headers = [h.strip().lower() for h in header_row.split('|') if h.strip()]
        
        # Parse table rows
        rows = table_body.strip().split('\n')
        for row in rows:
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if len(cells) < 2:  # Need at least name and reward
                continue
            
            # Map cells to columns based on header
            offer_data = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    offer_data[header] = cells[i]
            
            # Extract offer name (first column)
            offer_name = cells[0] if cells else ""
            
            # Extract reward value
            reward = ""
            for cell in cells:
                # Look for £ amounts
                amounts = re.findall(r'£(\d+(?:\.\d{2})?)', cell)
                if amounts:
                    reward = f"£{amounts[0]}"
                    break
            
            # Extract URL
            url = ""
            for cell in cells:
                found_url = extract_direct_url(cell)
                if found_url:
                    url = found_url
                    break
            
            # Extract requirements (last column or text after reward)
            requirements = ""
            if len(cells) > 2:
                requirements = cells[-1]
            elif len(cells) == 2:
                requirements = cells[1]
            
            if offer_name and reward:
                offers.append({
                    "store": offer_name[:40],
                    "item": offer_name[:80],
                    "deal_price": reward,
                    "link": url,
                    "requirements": requirements,
                    "type": "scraped_megalist",
                    "source": "MegaList",
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    return offers

def parse_list_items(text: str) -> List[Dict]:
    """
    Parse numbered or bulleted lists as fallback when no tables found.
    Format: 1. Offer Name - £50 reward (requirements)
    """
    offers = []
    
    # Pattern for numbered lists: 1. 2. 3. etc.
    numbered_pattern = r'^\d+[\.\)]\s+(.+?)(?=\n\d+[\.\)]|\n\n|$)'
    numbered_items = re.findall(numbered_pattern, text, re.MULTILINE | re.DOTALL)
    
    # Pattern for bulleted lists: • - * etc.
    bullet_pattern = r'^[•\-\*]\s+(.+?)(?=\n[•\-\*]|\n\n|$)'
    bullet_items = re.findall(bullet_pattern, text, re.MULTILINE | re.DOTALL)
    
    all_items = numbered_items + bullet_items
    
    for item_text in all_items:
        # Extract offer name (first few words before £ or -)
        name_match = re.match(r'^([^£\-]+?)(?=\s*[£\-]|$)', item_text)
        offer_name = name_match.group(1).strip() if name_match else item_text[:50].strip()
        
        # Extract reward
        reward = ""
        amounts = re.findall(r'£(\d+(?:\.\d{2})?)', item_text)
        if amounts:
            # Take the first valid amount (not highest)
            valid_amounts = []
            for amount in amounts:
                try:
                    amount_float = float(amount)
                    if 5 <= amount_float <= 1000:  # Reasonable range
                        valid_amounts.append(amount_float)
                except ValueError:
                    continue
            
            if valid_amounts:
                reward = f"£{valid_amounts[0]}"
        
        # Extract URL
        url = extract_direct_url(item_text)
        
        # Use the whole item as requirements
        requirements = item_text
        
        if offer_name and reward:
            offers.append({
                "store": offer_name[:40],
                "item": offer_name[:80],
                "deal_price": reward,
                "link": url,
                "requirements": requirements,
                "type": "scraped_megalist",
                "source": "MegaList",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return offers

def generate_ai_guide(offer_name: str, reward: str, requirements: str) -> str:
    """
    Generate a natural-sounding 3-step guide using pattern matching.
    Returns markdown formatted steps.
    """
    # Clean inputs
    requirements_lower = requirements.lower()
    offer_name_lower = offer_name.lower()
    
    # Step 1: Sign Up action
    sign_up_action = "Sign up"
    if "switch" in requirements_lower or "switch" in offer_name_lower:
        sign_up_action = "Switch account"
    elif "open" in requirements_lower or "open account" in requirements_lower:
        sign_up_action = "Open account"
    elif "deposit" in requirements_lower:
        sign_up_action = "Deposit funds"
    elif "invest" in requirements_lower:
        sign_up_action = "Invest"
    
    # Step 2: Specific action
    action_step = "Complete the required steps"
    
    # Extract specific actions
    if "deposit" in requirements_lower:
        deposit_match = re.search(r'deposit\s+£?(\d+(?:,\d{3})*(?:\.\d{2})?)', requirements_lower)
        if deposit_match:
            amount = deposit_match.group(1)
            action_step = f"Deposit £{amount}"
    
    if "spend" in requirements_lower:
        spend_match = re.search(r'spend\s+£?(\d+(?:,\d{3})*(?:\.\d{2})?)', requirements_lower)
        if spend_match:
            amount = spend_match.group(1)
            action_step = f"Spend £{amount}"
    
    if "switch" in requirements_lower:
        action_step = "Complete the Current Account Switch Service (CASS)"
    
    if "refer" in requirements_lower:
        action_step = "Refer friends (check specific requirements)"
    
    # Step 3: Reward timing
    reward_timing = "Receive your reward"
    
    # Extract timeframes
    timeframes = {
        "30 days": r'30\s+days|within\s+30\s+days',
        "60 days": r'60\s+days|within\s+60\s+days',
        "90 days": r'90\s+days|3\s+months',
        "immediate": r'immediate|instantly|right away',
        "few days": r'few\s+days|several\s+days',
        "7 days": r'7\s+days|within\s+a\s+week'
    }
    
    for timeframe, pattern in timeframes.items():
        if re.search(pattern, requirements_lower):
            reward_timing = f"Receive {reward} within {timeframe}"
            break
    
    # Format as markdown
    guide = f"""1. **{sign_up_action}** - Create an account using the provided link
2. **{action_step}** - Follow the specific requirements to qualify
3. **{reward_timing}** - The bonus will be paid once all conditions are met"""
    
    return guide

def scrape_reddit_post(url: str, visited_urls: Set[str] = None) -> List[Dict]:
    """
    Recursively scrape a Reddit post and follow sub-list links.
    Maintains visited_urls to prevent infinite loops.
    """
    if visited_urls is None:
        visited_urls = set()
    
    if url in visited_urls:
        return []
    
    visited_urls.add(url)
    offers = []
    
    print(f"📄 Scraping: {url}")
    
    try:
        headers = {
            "User-Agent": "MoneyHuntersUK/1.0 (contact: hello@moneyhunters.co.uk)"
        }
        response = requests.get(url + ".json", headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"   ⚠️ Failed to fetch: {response.status_code}")
            return offers
        
        data = response.json()
        post_data = data[0]['data']['children'][0]['data']
        post_body = post_data.get('selftext', '')
        
        # Parse markdown tables first (primary method)
        table_offers = parse_markdown_table(post_body)
        offers.extend(table_offers)
        
        # If no tables found, try parsing lists
        if not table_offers:
            list_offers = parse_list_items(post_body)
            offers.extend(list_offers)
        
        print(f"   ✅ Found {len(offers)} offers")
        
        # Look for sub-list links to crawl
        sublist_links = re.findall(r'\[([^\]]+)\]\((https://www\.reddit\.com/[^)]+)\)', post_body)
        
        for link_text, link_url in sublist_links:
            # Only follow links that look like offer guides/sub-lists
            guide_keywords = ['list', 'guide', 'offers', 'megathread', 'casino', 'bank', 'switch']
            if any(keyword in link_text.lower() for keyword in guide_keywords):
                # Ensure it's a full Reddit URL
                if link_url.startswith('https://www.reddit.com/'):
                    print(f"   🔗 Following sub-list: {link_text}")
                    time.sleep(1)  # Be polite
                    sub_offers = scrape_reddit_post(link_url, visited_urls)
                    offers.extend(sub_offers)
        
    except Exception as e:
        print(f"   ❌ Error scraping {url}: {e}")
    
    return offers

# ============================================
# DATA CLEANUP FUNCTIONS
# ============================================

def cleanup_old_offers(megalist_offers: List[Dict], existing_deals: List[Dict]) -> List[Dict]:
    """
    Remove ghost offers (old Reddit scraped offers not in MegaList).
    Preserve manual offers and supermarket deals.
    """
    # Create set of offer identifiers from MegaList
    megalist_keys = set()
    for offer in megalist_offers:
        key = f"{offer['store'].lower()}_{offer['deal_price']}"
        megalist_keys.add(key)
    
    cleaned_deals = []
    
    for deal in existing_deals:
        # Always keep manual offers (they have specific types)
        if deal.get('type') in ['bank_switch', 'referral', 'invest', 'cashback', 
                               'business', 'utilities', 'freebies', 'transfer', 
                               'credit', 'travel', 'pension']:
            cleaned_deals.append(deal)
            continue
        
        # Always keep supermarket deals
        if deal.get('category') == 'supermarket' or deal.get('type') == 'supermarket':
            cleaned_deals.append(deal)
            continue
        
        # For scraped Reddit offers, check if they're in MegaList
        if deal.get('source') == 'r/beermoneyuk' or deal.get('type') == 'scraped_reddit':
            deal_key = f"{deal['store'].lower()}_{deal['deal_price']}"
            if deal_key in megalist_keys:
                cleaned_deals.append(deal)
            else:
                print(f"   🗑️ Removing ghost offer: {deal['store']} - {deal['deal_price']}")
        else:
            # Keep other scraped offers (Google News, HotUKDeals)
            cleaned_deals.append(deal)
    
    return cleaned_deals

# ============================================
# MAIN SCRAPER FUNCTION
# ============================================

def scrape_megalist() -> List[Dict]:
    """
    Main function to scrape the MegaList and generate AI guides.
    """
    print("=" * 50)
    print("🤖 MEGALIST SCRAPER STARTING")
    print("=" * 50)
    
    # Target MegaList URL
    megalist_url = "https://www.reddit.com/r/beermoneyuk/comments/1rywry0/the_beermoney_megalist_march_2026_the_big_list_of/"
    
    # Recursively scrape MegaList and sub-lists
    all_offers = scrape_reddit_post(megalist_url)
    
    # Generate AI guides for each offer
    print("\n🤖 GENERATING AI STEP-BY-STEP GUIDES")
    for i, offer in enumerate(all_offers):
        guide = generate_ai_guide(
            offer['store'],
            offer['deal_price'],
            offer.get('requirements', '')
        )
        offer['step_by_step_guide'] = guide
        offer['steps'] = ["Follow the step-by-step guide below"]
        
        print(f"   [{i+1}/{len(all_offers)}] {offer['store']} - {offer['deal_price']} ✓ Guide generated")
    
    print(f"\n✅ Total MegaList offers: {len(all_offers)}")
    return all_offers

def run_enhanced_scraper() -> Dict:
    """
    Run the complete enhanced scraper with MegaList integration.
    """
    print("🛒 ENHANCED MONEY HUNTERS SCRAPER")
    print("=" * 50)
    
    all_deals = []
    
    # 1. Load existing deals to preserve manual offers
    try:
        with open("all_deals.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_deals = existing_data.get("deals", [])
        print(f"📦 Loaded {len(existing_deals)} existing deals")
    except:
        existing_deals = []
        print("📦 No existing deals found, starting fresh")
    
    # 2. Extract manual offers from existing data
    manual_offers = []
    supermarket_deals = []
    other_deals = []
    
    for deal in existing_deals:
        if deal.get('type') in ['bank_switch', 'referral', 'invest', 'cashback', 
                               'business', 'utilities', 'freebies', 'transfer', 
                               'credit', 'travel', 'pension']:
            manual_offers.append(deal)
        elif deal.get('category') == 'supermarket' or deal.get('type') == 'supermarket':
            supermarket_deals.append(deal)
        else:
            other_deals.append(deal)
    
    print(f"\n📊 Breakdown of existing data:")
    print(f"   - Manual offers: {len(manual_offers)}")
    print(f"   - Supermarket deals: {len(supermarket_deals)}")
    print(f"   - Other scraped offers: {len(other_deals)}")
    
    # 3. Scrape MegaList
    print("\n📡 SCRAPING MEGALIST")
    megalist_offers = scrape_megalist()
    
    # 4. Combine all offers
    all_deals.extend(manual_offers)
    all_deals.extend(supermarket_deals)
    all_deals.extend(megalist_offers)
    
    # 5. Clean up ghost offers
    print("\n🧹 CLEANING UP GHOST OFFERS")
    cleaned_deals = cleanup_old_offers(megalist_offers, all_deals)
    
    # 6. Add missing fields and calculate stacked prices
    for deal in cleaned_deals:
        #