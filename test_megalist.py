"""
Test MegaList Scraper - Dry Run
"""
import json
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Set

def extract_direct_url(text: str) -> str:
    """Extract destination URL, bypassing Reddit redirects."""
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
    for link_text, url in markdown_links:
        if 'out.reddit.com' in url or 'reddit.com/r/' in url:
            continue
        if re.match(r'https?://(?!.*reddit\.com)[\w\-\.]+\.[a-z]{2,}', url):
            return url
    
    raw_urls = re.findall(r'https?://[^\s\)]+', text)
    for url in raw_urls:
        if 'out.reddit.com' in url or 'reddit.com/r/' in url:
            continue
        if re.match(r'https?://(?!.*reddit\.com)[\w\-\.]+\.[a-z]{2,}', url):
            return url
    
    if markdown_links:
        return markdown_links[0][1]
    return ""

def parse_markdown_table(text: str) -> List[Dict]:
    """Parse markdown tables."""
    offers = []
    table_pattern = r'\|([^\n]+)\|\s*\n\|[-:]+\|\s*\n((?:\|[^\n]+\|\s*\n?)+)'
    tables = re.findall(table_pattern, text, re.MULTILINE)
    
    for header_row, table_body in tables:
        rows = table_body.strip().split('\n')
        for row in rows:
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if len(cells) < 2:
                continue
            
            offer_name = cells[0]
            reward = ""
            for cell in cells:
                amounts = re.findall(r'£(\d+(?:\.\d{2})?)', cell)
                if amounts:
                    reward = f"£{amounts[0]}"
                    break
            
            url = ""
            for cell in cells:
                found_url = extract_direct_url(cell)
                if found_url:
                    url = found_url
                    break
            
            requirements = cells[-1] if len(cells) > 2 else cells[1] if len(cells) == 2 else ""
            
            if offer_name and reward:
                offers.append({
                    "store": offer_name[:40],
                    "item": offer_name[:80],
                    "deal_price": reward,
                    "link": url,
                    "requirements": requirements,
                    "type": "scraped_megalist",
                    "source": "MegaList"
                })
    
    return offers

def parse_list_items(text: str) -> List[Dict]:
    """Parse numbered/bulleted lists."""
    offers = []
    numbered_pattern = r'^\d+[\.\)]\s+(.+?)(?=\n\d+[\.\)]|\n\n|$)'
    numbered_items = re.findall(numbered_pattern, text, re.MULTILINE | re.DOTALL)
    
    bullet_pattern = r'^[•\-\*]\s+(.+?)(?=\n[•\-\*]|\n\n|$)'
    bullet_items = re.findall(bullet_pattern, text, re.MULTILINE | re.DOTALL)
    
    all_items = numbered_items + bullet_items
    
    for item_text in all_items:
        name_match = re.match(r'^([^£\-]+?)(?=\s*[£\-]|$)', item_text)
        offer_name = name_match.group(1).strip() if name_match else item_text[:50].strip()
        
        reward = ""
        amounts = re.findall(r'£(\d+(?:\.\d{2})?)', item_text)
        if amounts:
            valid_amounts = []
            for amount in amounts:
                try:
                    amount_float = float(amount)
                    if 5 <= amount_float <= 1000:
                        valid_amounts.append(amount_float)
                except ValueError:
                    continue
            if valid_amounts:
                reward = f"£{valid_amounts[0]}"
        
        url = extract_direct_url(item_text)
        requirements = item_text
        
        if offer_name and reward:
            offers.append({
                "store": offer_name[:40],
                "item": offer_name[:80],
                "deal_price": reward,
                "link": url,
                "requirements": requirements,
                "type": "scraped_megalist",
                "source": "MegaList"
            })
    
    return offers

def generate_ai_guide(offer_name: str, reward: str, requirements: str) -> str:
    """Generate natural 3-step guide."""
    req_lower = requirements.lower()
    name_lower = offer_name.lower()
    
    # Step 1
    sign_up_action = "Sign up"
    if "switch" in req_lower or "switch" in name_lower:
        sign_up_action = "Switch account"
    elif "open" in req_lower or "open account" in req_lower:
        sign_up_action = "Open account"
    elif "deposit" in req_lower:
        sign_up_action = "Deposit funds"
    elif "invest" in req_lower:
        sign_up_action = "Invest"
    
    # Step 2
    action_step = "Complete the required steps"
    if "deposit" in req_lower:
        deposit_match = re.search(r'deposit\s+£?(\d+(?:,\d{3})*(?:\.\d{2})?)', req_lower)
        if deposit_match:
            action_step = f"Deposit £{deposit_match.group(1)}"
    elif "spend" in req_lower:
        spend_match = re.search(r'spend\s+£?(\d+(?:,\d{3})*(?:\.\d{2})?)', req_lower)
        if spend_match:
            action_step = f"Spend £{spend_match.group(1)}"
    elif "switch" in req_lower:
        action_step = "Complete the Current Account Switch Service (CASS)"
    elif "refer" in req_lower:
        action_step = "Refer friends (check specific requirements)"
    
    # Step 3
    reward_timing = "Receive your reward"
    timeframes = {
        "30 days": r'30\s+days|within\s+30\s+days',
        "60 days": r'60\s+days|within\s+60\s+days',
        "90 days": r'90\s+days|3\s+months',
        "immediate": r'immediate|instantly|right away',
        "few days": r'few\s+days|several\s+days',
        "7 days": r'7\s+days|within\s+a\s+week'
    }
    for timeframe, pattern in timeframes.items():
        if re.search(pattern, req_lower):
            reward_timing = f"Receive {reward} within {timeframe}"
            break
    
    return f"""1. **{sign_up_action}** - Create an account using the provided link
2. **{action_step}** - Follow the specific requirements to qualify
3. **{reward_timing}** - The bonus will be paid once all conditions are met"""

def scrape_reddit_post(url: str, visited_urls: Set[str] = None) -> List[Dict]:
    """Scrape Reddit post recursively."""
    if visited_urls is None:
        visited_urls = set()
    
    if url in visited_urls:
        return []
    
    visited_urls.add(url)
    offers = []
    
    print(f"📄 Scraping: {url}")
    
    try:
        headers = {"User-Agent": "MoneyHuntersUK/1.0"}
        response = requests.get(url + ".json", headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"   ⚠️ Failed: {response.status_code}")
            return offers
        
        data = response.json()
        post_body = data[0]['data']['children'][0]['data'].get('selftext', '')
        
        # Try tables first
        table_offers = parse_markdown_table(post_body)
        offers.extend(table_offers)
        
        # Fallback to lists
        if not table_offers:
            list_offers = parse_list_items(post_body)
            offers.extend(list_offers)
        
        print(f"   ✅ Found {len(offers)} offers")
        
        # Look for sub-list links
        sublist_links = re.findall(r'\[([^\]]+)\]\((https://www\.reddit\.com/[^)]+)\)', post_body)
        for link_text, link_url in sublist_links:
            guide_keywords = ['list', 'guide', 'offers', 'megathread', 'casino', 'bank', 'switch']
            if any(keyword in link_text.lower() for keyword in guide_keywords):
                if link_url.startswith('https://www.reddit.com/'):
                    print(f"   🔗 Following: {link_text}")
                    time.sleep(1)
                    sub_offers = scrape_reddit_post(link_url, visited_urls)
                    offers.extend(sub_offers)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return offers

def dry_run_test():
    """Run a dry test to show parsing logic."""
    print("🧪 DRY RUN TEST - MegaList Parser")
    print("=" * 50)
    
    test_url = "https://www.reddit.com/r/beermoneyuk/comments/1rywry0/the_beermoney_megalist_march_2026_the_big_list_of/"
    
    visited_urls = set()
    offers = scrape_reddit_post(test_url, visited_urls)
    
    # Generate AI guides for first 5 offers
    test_offers = offers[:5]
    for offer in test_offers:
        guide = generate_ai_guide(
            offer['store'],
            offer['deal_price'],
            offer.get('requirements', '')
        )
        offer['step_by_step_guide'] = guide
    
    print(f"\n✅ Dry run complete. Found {len(offers)} offers.")
    print(f"📊 Showing first {len(test_offers)} offers with AI guides:")
    print("=" * 50)
    
    for i, offer in enumerate(test_offers):
        print(f"\n{i+1}. {offer['store']} - {offer['deal_price']}")
        print(f"   Link: {offer.get('link', 'No link')}")
        if offer.get('requirements'):
            print(f"   Requirements: {offer['requirements'][:100]}...")
        print(f"   AI Guide:")
        print(f"   {offer['step_by_step_guide']}")
        print("-" * 40)
    
    return test_offers

if __name__ == "__main__":
    dry_run_test()