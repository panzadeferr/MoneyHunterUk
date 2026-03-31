#!/usr/bin/env python3
"""
Scrimpr HTML Parser for Money Hunters UK

Purpose:
- Parse the saved Scrimpr 'Free Money' page (scrimpr.html)
- Extract 131 deals from offer blocks (wp-block-group or headers containing 'Your Reward')
- Save extracted deals to megalist.json with type: "scraped_megalist"
- Prefix IDs with 'sc_' to prevent conflicts with manual deals
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
SCRIMPR_HTML_PATH = BASE_DIR / "test_scrimpr.html"  # Changed to test file
MEGALIST_JSON_PATH = BASE_DIR / "megalist.json"

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_first_two_sentences(text: str) -> str:
    """Extract first 2 sentences for the desc field."""
    text = normalize_text(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) >= 2:
        return ' '.join(sentences[:2])
    return text

def format_step_guide(description: str) -> str:
    """Format description as a clean step-guide string."""
    desc = extract_first_two_sentences(description)
    # Clean up common patterns
    desc = re.sub(r'\s+', ' ', desc)
    desc = desc.strip()
    return desc

def extract_reward_amount(text: str) -> Tuple[str, float]:
    """Extract reward amount from text."""
    text = normalize_text(text)
    # Look for £ amounts
    matches = re.findall(r'£\s?(\d+(?:,\d{3})*(?:\.\d{1,2})?)', text)
    if matches:
        try:
            amount = float(matches[0].replace(',', ''))
            return f"£{amount:.2f}".rstrip('0').rstrip('.'), amount
        except ValueError:
            pass
    
    # Look for free/share/bonus keywords
    lower = text.lower()
    if 'free share' in lower:
        return 'Free Share', 0.0
    if 'free coffee' in lower or 'free tea' in lower:
        return 'Free Drink', 0.0
    if 'free month' in lower:
        return 'Free Month', 0.0
    if 'gift card' in lower:
        return 'Gift Card', 0.0
    if 'bonus' in lower:
        return 'Bonus', 0.0
    
    return 'Reward', 0.0

def generate_scrimpr_id(store: str, reward: str, link: str) -> str:
    """Generate unique ID prefixed with 'sc_' for Scrimpr deals."""
    seed = f"{store}|{reward}|{link}".strip().lower()
    # Create a base slug
    base = re.sub(r'[^a-z0-9]+', '-', store.lower())[:40]
    # Add hash for uniqueness
    digest = hashlib.md5(seed.encode('utf-8')).hexdigest()[:8]
    return f"sc_{base}-{digest}"

def infer_category(store: str, description: str) -> str:
    """Infer category from store name and description."""
    combined = f"{store} {description}".lower()
    
    if any(kw in combined for kw in ['bank', 'switch', 'lloyds', 'chase', 'monzo', 'revolut', 'zopa', 'halifax', 'natwest', 'barclays', 'santander', 'first direct', 'starling']):
        return 'bank_switch'
    if any(kw in combined for kw in ['invest', 'share', 'freetrade', 'robinhood', 'wealthify', 'wealthyhood', 'webull', 'fidelity', 'nutmeg', 'pension']):
        return 'investment'
    if any(kw in combined for kw in ['cashback', 'quidco', 'rakuten', 'topcashback', 'gemsloot', 'cashinstyle']):
        return 'cashback'
    if any(kw in combined for kw in ['business', 'worldfirst', 'tide', 'amex business']):
        return 'business'
    if any(kw in combined for kw in ['transfer', 'wise', 'skrill']):
        return 'transfer'
    if any(kw in combined for kw in ['energy', 'octopus', 'utility', 'mobile', 'lebara']):
        return 'utilities'
    if any(kw in combined for kw in ['free coffee', 'free cake', 'free box', 'free month', 'freebie']):
        return 'freebies'
    if any(kw in combined for kw in ['tesco', 'asda', 'sainsbury', 'waitrose', 'morrisons', 'iceland', 'aldi', 'lidl']):
        return 'supermarket'
    
    return 'other'

def build_steps(description: str, category: str) -> List[str]:
    """Build step-by-step guide from description."""
    desc = normalize_text(description)
    
    # Generic steps that can be customized
    if category == 'bank_switch':
        return [
            "Open the account using the referral link",
            "Complete the switch or signup requirements",
            "Wait for the cash reward to be paid"
        ]
    elif category == 'investment':
        return [
            "Open the investing account via the link",
            "Deposit or invest the qualifying amount",
            "Hold or claim the reward when terms are met"
        ]
    elif category == 'cashback':
        return [
            "Create the cashback/rewards account",
            "Complete the qualifying purchase or task",
            "Track and claim the reward once confirmed"
        ]
    elif category == 'business':
        return [
            "Open the business account or card",
            "Complete the qualifying spend or switch",
            "Wait for the bonus to be paid"
        ]
    else:
        return [
            "Open the latest offer link",
            "Follow the current provider requirements",
            "Claim your reward when eligible"
        ]

def parse_scrimpr_html() -> List[Dict]:
    """Parse scrimpr.html and extract deals."""
    if not SCRIMPR_HTML_PATH.exists():
        print(f"Error: {SCRIMPR_HTML_PATH} not found!")
        print("Please save the Scrimpr 'Free Money' page as scrimpr.html in the current directory.")
        return []
    
    print(f"Reading {SCRIMPR_HTML_PATH}...")
    html_content = SCRIMPR_HTML_PATH.read_text(encoding='utf-8', errors='ignore')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    deals = []
    
    # Strategy 1: Look for wp-block-group elements (common in WordPress)
    wp_blocks = soup.find_all(class_=re.compile(r'wp-block-group'))
    print(f"Found {len(wp_blocks)} wp-block-group elements")
    
    # Strategy 2: Look for headers containing 'Your Reward' or similar
    reward_headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], 
                                   string=re.compile(r'Your Reward|Reward|Bonus|Get £', re.I))
    print(f"Found {len(reward_headers)} reward headers")
    
    # Strategy 3: Look for offer containers - common patterns
    offer_containers = []
    
    # Try common class names
    for class_name in ['offer', 'deal', 'card', 'promotion', 'bonus', 'reward']:
        containers = soup.find_all(class_=re.compile(class_name, re.I))
        offer_containers.extend(containers)
    
    # Remove duplicates
    seen_elements = set()
    unique_containers = []
    for container in offer_containers:
        if container not in seen_elements:
            seen_elements.add(container)
            unique_containers.append(container)
    
    print(f"Found {len(unique_containers)} unique offer containers")
    
    # Combine all potential offer blocks
    all_blocks = list(wp_blocks) + list(reward_headers) + unique_containers
    
    # If we don't find enough blocks, try a more aggressive approach
    if len(all_blocks) < 50:
        print("Not enough blocks found, trying broader search...")
        # Look for any div with text containing £
        money_divs = soup.find_all(text=re.compile(r'£\d+'))
        parent_divs = set()
        for text in money_divs:
            parent = text.find_parent('div')
            if parent:
                parent_divs.add(parent)
        all_blocks.extend(list(parent_divs))
        print(f"Added {len(parent_divs)} money-containing divs")
    
    # Process each block to extract deals
    for block in all_blocks[:200]:  # Limit to avoid too many false positives
        try:
            # Extract store name - look for strong/bold text or headers
            store_elem = block.find(['strong', 'b', 'h1', 'h2', 'h3', 'h4'])
            store = normalize_text(store_elem.get_text() if store_elem else '')
            
            if not store:
                # Try to find store name in the block text
                block_text = normalize_text(block.get_text())
                # Look for patterns like "**Store Name**" or similar
                bold_match = re.search(r'\*\*(.+?)\*\*', block_text)
                if bold_match:
                    store = bold_match.group(1).strip()
                else:
                    # Take first few words as store name
                    words = block_text.split()
                    if len(words) > 2:
                        store = ' '.join(words[:2])
                    else:
                        store = block_text[:30]
            
            # Extract reward amount
            block_text = normalize_text(block.get_text())
            reward_str, reward_amount = extract_reward_amount(block_text)
            
            # Extract link
            link_elem = block.find('a', href=True)
            link = link_elem['href'] if link_elem else ''
            
            # Skip if no link or no meaningful store name
            if not link or not store or len(store) < 2:
                continue
            
            # Extract description (use block text)
            description = block_text
            
            # Generate ID with sc_ prefix
            deal_id = generate_scrimpr_id(store, reward_str, link)
            
            # Infer category
            category = infer_category(store, description)
            
            # Build steps
            steps = build_steps(description, category)
            
            # Create deal object
            deal = {
                "id": deal_id,
                "store": store[:60],
                "item": extract_first_two_sentences(description)[:120],
                "deal_price": reward_str,
                "link": link,
                "requirements": description[:200],
                "step_by_step_guide": "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps)),
                "steps": steps,
                "type": "scraped_megalist",
                "source": "Scrimpr Free Money",
                "category": category,
                "code": "",
                "last_updated": now_str(),
                "desc": format_step_guide(description)
            }
            
            deals.append(deal)
            
        except Exception as e:
            # Skip blocks that cause errors
            continue
    
    # Deduplicate by link
    unique_deals = []
    seen_links = set()
    for deal in deals:
        if deal['link'] and deal['link'] not in seen_links:
            seen_links.add(deal['link'])
            unique_deals.append(deal)
    
    print(f"Extracted {len(unique_deals)} unique deals from Scrimpr HTML")
    return unique_deals

def save_megalist(deals: List[Dict]) -> None:
    """Save deals to megalist.json."""
    output = {
        "last_updated": now_str(),
        "total_deals": len(deals),
        "source": "Scrimpr Free Money Page",
        "type": "scraped_megalist",
        "deals": deals
    }
    
    MEGALIST_JSON_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    print(f"Saved {len(deals)} deals to {MEGALIST_JSON_PATH}")

def main():
    """Main function to parse Scrimpr HTML and save to megalist.json."""
    print("=" * 60)
    print("Scrimpr HTML Parser for Money Hunters UK")
    print("=" * 60)
    
    deals = parse_scrimpr_html()
    
    if deals:
        save_megalist(deals)
        print(f"\nSuccessfully extracted {len(deals)} deals!")
        print(f"Output saved to: {MEGALIST_JSON_PATH}")
        
        # Show sample of first 3 deals
        print("\nSample deals (first 3):")
        for i, deal in enumerate(deals[:3]):
            print(f"\n{i+1}. {deal['store']} - {deal['deal_price']}")
            print(f"   ID: {deal['id']}")
            print(f"   Category: {deal['category']}")
            print(f"   Link: {deal['link'][:80]}...")
    else:
        print("\nNo deals extracted. Please check:")
        print(f"1. Is {SCRIMPR_HTML_PATH} in the current directory?")
        print("2. Does the file contain the Scrimpr 'Free Money' page?")
        print("3. Is the HTML structure readable?")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()