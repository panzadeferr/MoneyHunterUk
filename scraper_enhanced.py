"""
Enhanced Money Hunters Scraper with MegaList Integration
- Parses markdown tables from MegaList
- Deep crawls sub-list links
- Generates AI step-by-step guides
- Cleans up ghost offers
"""

import json
import os
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin

# ============================================
# TELEGRAM SETUP (Optional) - Keep existing
# ============================================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_to_telegram(deal: Dict) -> bool:
    """Send a deal to Telegram channel"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        message = f"""
🛒 *{deal['store']}* - {deal['item']}
💰 Deal Price: {deal['deal_price']}
📊 Stacked Price: *£{deal.get('stacked_price', 0):.2f}*
💡 Save with {deal.get('best_payment_method', 'N/A')}
🔗 {deal['link']}
        """.strip()
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

# ============================================
# STACKING RATES (Per Store) - Keep existing
# ============================================

STACKING_RATES = {
    "Tesco": 5.3,
    "Sainsbury's": 4.4,
    "Asda": 4.5,
    "Iceland": 5.0,
    "Morrisons": 4.0,
    "Waitrose": 3.5,
    "Aldi": 2.0,
    "Lidl": 2.0
}

BEST_PAYMENT = {
    "Tesco": "EverUp (4.9%) + Clubcard",
    "Sainsbury's": "JamDoughnut (4.1%) + Nectar",
    "Asda": "Airtime Rewards (4%) + Asda Rewards",
    "Iceland": "TopCashback (3.5%) + Bonus Card",
    "Morrisons": "Cheddar (3%) + More Card",
    "Waitrose": "JamDoughnut (3.5%) + MyWaitrose",
    "Aldi": "No gift cards, but use cashback credit card",
    "Lidl": "No gift cards, but use cashback credit card"
}

# ============================================
# 30+ MANUAL OFFERS (Bank Switches, Referrals, Cashback)
# ============================================

def get_manual_offers() -> List[Dict]:
    """All your original BeermoneyUK offers"""
    return [
        # BANK SWITCH OFFERS
        {"store": "Lloyds Bank", "item": "Open Account + Switch", "deal_price": "£250", "link": "https://apply.lloydsbank.co.uk/sales-content/cwa/l/onboardpca/index-app.html?from=ob&webDirect=true&redesign=true&token=JpGVwskEUPxoFpO3Mg4RTAUZg6q6Emjz578QtNaABT8=&redesign=true#/refer-friend", "original_price": "£0", "saving_percent": 100, "type": "bank_switch", "code": "", "steps": ["Open account", "Switch using CASS", "Get £250"], "timeFrame": "30 days"},
        {"store": "Chase UK", "item": "Deposit £1,000 → £50", "deal_price": "£50", "link": "https://chase.co.uk/raf", "original_price": "£0", "saving_percent": 100, "type": "bank_switch", "code": "J2SK9W", "steps": ["Copy code J2SK9W", "Open account", "Deposit £1,000 in 30 days"], "timeFrame": "30 days"},
        {"store": "Monzo", "item": "Spend £1 → Get £5-£50", "deal_price": "£5-£50", "link": "https://join.monzo.com/r/", "original_price": "£1", "saving_percent": 90, "type": "referral", "code": "", "steps": ["Sign up", "Spend £1", "Get bonus"], "timeFrame": "Immediate"},
        {"store": "Revolut", "item": "Spend £1 → Get £20", "deal_price": "£20", "link": "https://revolut.com/referral/?referral-code=ludoviv2sq!MAR1-26-AR-H2&geo-redirect", "original_price": "£1", "saving_percent": 95, "type": "referral", "code": "", "steps": ["Sign up", "Spend £1", "Get £20"], "timeFrame": "~1 month"},
        {"store": "First Direct", "item": "Switch Account → £175", "deal_price": "£175", "link": "https://www.firstdirect.com/banking/switch/", "original_price": "£0", "saving_percent": 100, "type": "bank_switch", "code": "", "steps": ["Switch using CASS", "Pay in £1,000", "Get £175"], "timeFrame": "30 days"},
        {"store": "Halifax", "item": "Switch Account → £150", "deal_price": "£150", "link": "https://www.halifax.co.uk/currentaccounts/", "original_price": "£0", "saving_percent": 100, "type": "bank_switch", "code": "", "steps": ["Switch using CASS", "Pay in £1,500", "Get £150"], "timeFrame": "30 days"},
        {"store": "NatWest", "item": "Switch Account → £200", "deal_price": "£200", "link": "https://www.natwest.com/current-accounts/switch/", "original_price": "£0", "saving_percent": 100, "type": "bank_switch", "code": "", "steps": ["Switch using CASS", "2 direct debits", "Get £200"], "timeFrame": "30 days"},
        
        # INVESTMENT OFFERS
        {"store": "Freetrade", "item": "Deposit £1 → Free Share (£10-£100)", "deal_price": "£10-£100", "link": "https://magic.freetrade.io/join/alberto/6f308795", "original_price": "£1", "saving_percent": 90, "type": "invest", "code": "", "steps": ["Deposit £1", "Get free share"], "timeFrame": "Few days"},
        {"store": "Robinhood", "item": "Deposit £1 → Free Share", "deal_price": "£10-£140", "link": "https://join.robinhood.com/albertb-d5dfe0", "original_price": "£1", "saving_percent": 90, "type": "invest", "code": "", "steps": ["Deposit £1", "Get free share"], "timeFrame": "Few days"},
        {"store": "Plum", "item": "Refer 3 Friends → £75", "deal_price": "£75", "link": "https://friends.withplum.com/r/RxK7c2fUNa", "original_price": "£0", "saving_percent": 100, "type": "invest", "code": "", "steps": ["Join Plum", "Refer 3 friends", "Get £75"], "timeFrame": "Expires April 7th"},
        {"store": "Webull", "item": "Deposit £500 → £50 Credit", "deal_price": "£50", "link": "https://www.webull-uk.com/s/zEUukbJam8GjmUx6yq", "original_price": "£500", "saving_percent": 10, "type": "invest", "code": "", "steps": ["Deposit £500", "Keep 60 days", "Get £50"], "timeFrame": "60 days"},
        {"store": "Wealthify", "item": "Invest £1,000 → £50 Bonus", "deal_price": "£50", "link": "https://invest.wealthify.com/refer/81122944", "original_price": "£1,000", "saving_percent": 5, "type": "invest", "code": "", "steps": ["Invest £1,000", "Hold 6 months", "Get £50"], "timeFrame": "6 months"},
        {"store": "Moneybox", "item": "Save & Invest - Great for DDs", "deal_price": "Bonus", "link": "https://go.onelink.me/5M0L?pid=share&c=EN8YW8", "original_price": "£0", "saving_percent": 0, "type": "invest", "code": "", "steps": ["Download Moneybox", "Perfect for direct debits"], "timeFrame": "Ongoing"},
        
        # CASHBACK SITES
        {"store": "TopCashback", "item": "Cashback Site - £10 Bonus", "deal_price": "£10", "link": "https://www.topcashback.co.uk/ref/Panzadeferr/?source_id=4", "original_price": "£0", "saving_percent": 100, "type": "cashback", "code": "", "steps": ["Join TopCashback", "Shop through site"], "timeFrame": "Lifetime"},
        {"store": "Quidco", "item": "Cashback Site - £20 Bonus", "deal_price": "£20", "link": "https://quidco.onelink.me/nKzg/v2f3f7m0", "original_price": "£0", "saving_percent": 100, "type": "cashback", "code": "", "steps": ["Join Quidco", "Earn £5 cashback", "Get £20"], "timeFrame": "After earning £5"},
        {"store": "Rakuten", "item": "Cashback Site - £25 Bonus", "deal_price": "£25", "link": "https://www.rakuten.co.uk/r/ALBERT24541?eeid=28187", "original_price": "£50", "saving_percent": 50, "type": "cashback", "code": "", "steps": ["Join Rakuten", "Spend £50 + VAT", "Get £25"], "timeFrame": "After first purchase"},
        
        # GIFT CARD APPS
        {"store": "Airtime", "item": "Gift Card Cashback - £2 Bonus", "deal_price": "£2", "link": "https://airtimerewards.app.link/6Waa7E1IF1b", "original_price": "£5", "saving_percent": 40, "type": "cashback", "code": "FRJKFXX3", "steps": ["Use code FRJKFXX3", "Spend £5 in 7 days", "Get £2"], "timeFrame": "7 days"},
        {"store": "Cheddar", "item": "Gift Card Cashback - £3 Bonus", "deal_price": "£3", "link": "https://get.cheddar.me/app/FVESBGB", "original_price": "£0", "saving_percent": 100, "type": "cashback", "code": "FVESBGB", "steps": ["Use code FVESBGB", "Earn cashback at retailers"], "timeFrame": "Ongoing"},
        {"store": "Jam Doughnut", "item": "Gift Card Cashback - £3 Bonus", "deal_price": "£3", "link": "https://www.jamdoughnut.com/", "original_price": "£0", "saving_percent": 100, "type": "cashback", "code": "8TGF", "steps": ["Use code 8TGF", "Buy gift cards with cashback"], "timeFrame": "Immediate"},
        {"store": "EverUp", "item": "Gift Card Cashback", "deal_price": "£2", "link": "https://everup.onelink.me/9lgD/3d22pmln", "original_price": "£0", "saving_percent": 100, "type": "cashback", "code": "", "steps": ["Join EverUp", "Link cards", "Earn cashback"], "timeFrame": "Ongoing"},
        
        # BUSINESS ACCOUNTS
        {"store": "Tide", "item": "Business Account - £75 Free", "deal_price": "£75", "link": "https://www.tide.co/", "original_price": "£0", "saving_percent": 100, "type": "business", "code": "3834VA", "steps": ["Sign up for Tide", "Use code 3834VA", "Make first transaction"], "timeFrame": "After first transaction"},
        {"store": "WorldFirst", "item": "Business - Up to £355 Reward", "deal_price": "£355", "link": "https://s.worldfirst.com/2TuviC?default_source=WF-Ts00000OCun2&referral_id=WF-Ts00000OCun2&utm_campaign=COE_MGM_UK_2602&utm_date=app&lang=en_GB", "original_price": "£0", "saving_percent": 100, "type": "business", "code": "", "steps": ["Open WorldFirst", "Make qualifying transactions", "Get up to £355"], "timeFrame": "Varies"},
        
        # UTILITIES
        {"store": "Octopus Energy", "item": "Switch Energy - £50 Credit", "deal_price": "£50", "link": "https://share.octopus.energy/ocean-quoll-258", "original_price": "£0", "saving_percent": 100, "type": "utilities", "code": "", "steps": ["Switch to Octopus", "Use referral link", "Both get £50"], "timeFrame": "After switch"},
        {"store": "Lebara", "item": "Mobile SIM - Referral Bonus", "deal_price": "Discount", "link": "https://aklam.io/hgY3HOvR", "original_price": "£0", "saving_percent": 20, "type": "utilities", "code": "", "steps": ["Sign up for Lebara", "Get great SIM deals"], "timeFrame": "Immediate"},
        
        # FREEBIES
        {"store": "Costa", "item": "Free Cake + Coffee", "deal_price": "Free", "link": "https://www.costa.co.uk/", "original_price": "£5", "saving_percent": 100, "type": "freebies", "code": "", "steps": ["Sign up for Costa Club", "Get free cake & half drink"], "timeFrame": "Immediate"},
        {"store": "Waitrose", "item": "Free Coffee Daily", "deal_price": "Free", "link": "https://www.waitrose.com/", "original_price": "£3", "saving_percent": 100, "type": "freebies", "code": "", "steps": ["Get Waitrose card", "Free tea/coffee daily"], "timeFrame": "Daily"},
        
        # MONEY TRANSFER
        {"store": "Wise", "item": "Free Transfer + Card", "deal_price": "Free", "link": "https://wise.com/invite/ahpc/albertob1508", "original_price": "£5", "saving_percent": 100, "type": "transfer", "code": "", "steps": ["Sign up for Wise", "First transfer free", "Get free card"], "timeFrame": "Immediate"},
        
        # CREDIT CARD
        {"store": "AMEX", "item": "Spend £3,000 → £150+", "deal_price": "£150", "link": "https://americanexpress.com/en-gb/referral/platinum-charge?ref=aLBERBf3Ob&XL=MNMNS", "original_price": "£0", "saving_percent": 100, "type": "credit", "code": "", "steps": ["Apply for AMEX", "Spend £3,000 in 3 months", "Get £150"], "timeFrame": "3 months"},
        
        # TRAVEL
        {"store": "TrainPal", "item": "£3 Off Train Tickets", "deal_price": "£3", "link": "https://t.trainpal.com/wUEPLNq", "original_price": "£0", "saving_percent": 100, "type": "travel", "code": "03ba089c$00", "steps": ["Download TrainPal", "Use code 03ba089c$00", "Save on train tickets"], "timeFrame": "Use within 7 days"},
        
        # OTHER REFERRALS
        {"store": "Zilch", "item": "Sign Up → £5 Free", "deal_price": "£5", "link": "https://zilch.onelink.me/x