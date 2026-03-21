"""
Multi-Supermarket Deal Scraper with Stacked Prices
Runs daily via GitHub Actions, sends best deals to Telegram
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict

# ============================================
# TELEGRAM SETUP (will use GitHub Secrets)
# ============================================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_to_telegram(deal: Dict) -> bool:
    """
    Send a deal to Telegram channel using Bot
    Returns True if sent successfully
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not set. Skipping...")
        return False

    try:
        import requests

        # Format message
        message = f"""
🛒 *{deal['store']}* - {deal['item']}
💰 Original: {deal.get('original_price', 'Varies')}
🎁 Deal Price: {deal['deal_price']}
📊 Stacked Price: *£{deal['stacked_price']:.2f}*
💡 Save {deal['saving_percent']}% with {deal['best_payment_method']}

🔗 {deal['link']}
        """.strip()

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200

    except Exception as e:
        print(f"❌ Telegram send failed: {e}")
        return False


# ============================================
# STACKING RATES (Per Store)
# ============================================

STACKING_RATES = {
    "Tesco": 5.3,      # EverUp (4.9%) + Clubcard points
    "Sainsbury's": 4.4,  # JamDoughnut (4.1%) + Nectar points
    "Asda": 4.5,        # Airtime (4%) + Asda Rewards
    "Iceland": 5.0      # TopCashback (3.5%) + Bonus Card offers
}

BEST_PAYMENT = {
    "Tesco": "EverUp Gift Card (4.9%) + Clubcard",
    "Sainsbury's": "JamDoughnut (4.1%) + Nectar",
    "Asda": "Airtime Rewards (4%) + Asda Rewards",
    "Iceland": "TopCashback (3.5%) + Bonus Card"
}


# ============================================
# DEAL DATABASE (Manual for now - upgrade later)
# ============================================

def get_tesco_deals() -> List[Dict]:
    """Get Tesco deals - can be upgraded with Playwright later"""
    return [
        {
            "store": "Tesco",
            "item": "Clubcard Prices - Selected Items",
            "original_price": "Varies",
            "deal_price": "Up to 50% off",
            "link": "https://www.tesco.com/clubcard/prices/",
            "saving_percent": 50,
            "base_price": 20  # Example price for stacking calculation
        },
        {
            "store": "Tesco",
            "item": "Fresh Meat & Fish",
            "original_price": "£10.00",
            "deal_price": "£7.00",
            "link": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/all",
            "saving_percent": 30,
            "base_price": 7
        },
        {
            "store": "Tesco",
            "item": "Wine Selection - 6 Bottles",
            "original_price": "£42.00",
            "deal_price": "£30.00",
            "link": "https://www.tesco.com/groceries/en-GB/shop/drinks/wine/all",
            "saving_percent": 29,
            "base_price": 30
        }
    ]


def get_asda_deals() -> List[Dict]:
    """Get Asda deals"""
    return [
        {
            "store": "Asda",
            "item": "Payday Deals - Selected Items",
            "original_price": "Varies",
            "deal_price": "Up to 40% off",
            "link": "https://www.asda.com/deals",
            "saving_percent": 40,
            "base_price": 15
        },
        {
            "store": "Asda",
            "item": "Fresh Fruit & Vegetables - Mix & Match",
            "original_price": "£3.50",
            "deal_price": "£2.50",
            "link": "https://groceries.asda.com/deals/fresh-food",
            "saving_percent": 29,
            "base_price": 2.5
        },
        {
            "store": "Asda",
            "item": "Household Essentials Bundle",
            "original_price": "£8.00",
            "deal_price": "£5.50",
            "link": "https://groceries.asda.com/deals/household",
            "saving_percent": 31,
            "base_price": 5.5
        }
    ]


def get_sainsburys_deals() -> List[Dict]:
    """Get Sainsbury's deals"""
    return [
        {
            "store": "Sainsbury's",
            "item": "Nectar Prices - Members Only",
            "original_price": "Varies",
            "deal_price": "Exclusive Nectar prices",
            "link": "https://www.sainsburys.co.uk/nectar-prices",
            "saving_percent": 25,
            "base_price": 12
        },
        {
            "store": "Sainsbury's",
            "item": "Fresh Bakery - 2 for £3",
            "original_price": "£3.50",
            "deal_price": "£3.00",
            "link": "https://www.sainsburys.co.uk/groceries/bakery",
            "saving_percent": 14,
            "base_price": 3
        },
        {
            "store": "Sainsbury's",
            "item": "Meal Deal - Lunch",
            "original_price": "£5.00",
            "deal_price": "£3.50",
            "link": "https://www.sainsburys.co.uk/meal-deal",
            "saving_percent": 30,
            "base_price": 3.5
        }
    ]


def get_iceland_deals() -> List[Dict]:
    """Get Iceland deals"""
    return [
        {
            "store": "Iceland",
            "item": "3 for £10 - Selected Frozen",
            "original_price": "£15.00",
            "deal_price": "£10.00",
            "link": "https://www.iceland.co.uk/offers",
            "saving_percent": 33,
            "base_price": 10
        },
        {
            "store": "Iceland",
            "item": "Bonus Club Offers - Members Only",
            "original_price": "Varies",
            "deal_price": "Members-only prices",
            "link": "https://www.iceland.co.uk/bonus-card",
            "saving_percent": 20,
            "base_price": 8
        },
        {
            "store": "Iceland",
            "item": "Family Favourites Bundle",
            "original_price": "£12.00",
            "deal_price": "£8.00",
            "link": "https://www.iceland.co.uk/family-meals",
            "saving_percent": 33,
            "base_price": 8
        }
    ]


# ============================================
# CALCULATE STACKED PRICE
# ============================================

def calculate_stacked_price(deal: Dict) -> float:
    """
    Calculate the real price after stacking discounts
    Uses store-specific stacking rates
    """
    store = deal["store"]
    base_price = deal.get("base_price", 0)

    # Try to extract price from deal_price string if base_price not set
    if base_price == 0 and "£" in deal["deal_price"]:
        import re
        match = re.search(r'£(\d+(?:\.\d{2})?)', deal["deal_price"])
        if match:
            base_price = float(match.group(1))

    if base_price == 0:
        return 0

    stacking_rate = STACKING_RATES.get(store, 4.0)
    savings = base_price * (stacking_rate / 100)
    return round(base_price - savings, 2)


# ============================================
# MAIN SCRAPER FUNCTION
# ============================================

def run_all_scrapers() -> Dict:
    """Run all scrapers and save results"""
    print("🛒 Supermarket Deal Scraper Starting...")
    print("=" * 50)

    all_deals = []

    # Run each scraper
    print("\n📦 Fetching Tesco deals...")
    tesco_deals = get_tesco_deals()
    all_deals.extend(tesco_deals)
    print(f"   Found {len(tesco_deals)} deals")

    print("\n📦 Fetching Asda deals...")
    asda_deals = get_asda_deals()
    all_deals.extend(asda_deals)
    print(f"   Found {len(asda_deals)} deals")

    print("\n📦 Fetching Sainsbury's deals...")
    sainsburys_deals = get_sainsburys_deals()
    all_deals.extend(sainsburys_deals)
    print(f"   Found {len(sainsburys_deals)} deals")

    print("\n📦 Fetching Iceland deals...")
    iceland_deals = get_iceland_deals()
    all_deals.extend(iceland_deals)
    print(f"   Found {len(iceland_deals)} deals")

    # Calculate stacked prices and add best payment method
    best_deals = []
    for deal in all_deals:
        stacked_price = calculate_stacked_price(deal)
        deal["stacked_price"] = stacked_price
        deal["best_payment_method"] = BEST_PAYMENT.get(deal["store"], "Gift card + loyalty")
        deal["stacking_rate"] = STACKING_RATES.get(deal["store"], 4.0)
        deal["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if stacked_price > 0:
            best_deals.append(deal)

    # Sort by stacked price (cheapest first)
    best_deals.sort(key=lambda x: x["stacked_price"] if x["stacked_price"] > 0 else 999)

    # Save all deals to JSON
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_deals": len(all_deals),
        "stacking_rates": STACKING_RATES,
        "deals": all_deals,
        "best_deals": best_deals[:10]  # Top 10 best value deals
    }

    with open("all_deals.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("-" * 40)
    print(f"✅ Total deals found: {len(all_deals)}")
    print(f"💾 Saved to all_deals.json")

    # Send top 3 deals to Telegram
    print("\n📱 Sending top deals to Telegram...")
    for i, deal in enumerate(best_deals[:3]):
        if deal["stacked_price"] > 0:
            success = send_to_telegram(deal)
            if success:
                print(f"   ✅ Sent: {deal['store']} - £{deal['stacked_price']}")
            else:
                print(f"   ⚠️ Failed to send: {deal['store']}")
            time.sleep(1)  # Avoid rate limiting

    print("=" * 50)
    return output


# ============================================
# RUN THE SCRAPER
# ============================================

if __name__ == "__main__":
    run_all_scrapers()