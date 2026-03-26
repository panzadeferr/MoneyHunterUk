import requests
import schedule
import time
import os
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHANNEL    = "@MoneyHunterUK"
APP_URL    = "https://moneyhunters.co.uk"
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_LIST_ID = 2

# --- STARTUP SAFETY CHECK ---
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set. Add it to Railway Variables.")
if not BREVO_API_KEY:
    print("⚠️  WARNING: BREVO_API_KEY not set. Email subscriptions will not work.")

# --- FLASK APP ---
app = Flask(__name__)
CORS(app, origins=["https://moneyhunters.co.uk", "https://www.moneyhunters.co.uk"])

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "Money Hunters UK"})

@app.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        data = request.get_json()
        email = (data.get("email") or "").strip()
        first_name = (data.get("firstName") or "").strip()
        username = (data.get("username") or "").strip()
        if not email or "@" not in email:
            return jsonify({"error": "Invalid email"}), 400
        if not BREVO_API_KEY:
            return jsonify({"error": "Not configured"}), 500
        resp = requests.post(
            "https://api.brevo.com/v3/contacts",
            headers={"Content-Type": "application/json", "api-key": BREVO_API_KEY},
            json={
                "email": email,
                "listIds": [BREVO_LIST_ID],
                "updateEnabled": True,
                "attributes": {"FIRSTNAME": first_name, "USERNAME": username, "SOURCE": "Money Hunters App"}
            },
            timeout=10
        )
        if resp.status_code in (200, 201, 204):
            print(f"✅ New subscriber: {email}")
            return jsonify({"success": True}), 200
        elif "duplicate" in resp.text.lower():
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Subscription failed"}), 500
    except Exception as e:
        print(f"Subscribe error: {e}")
        return jsonify({"error": "Server error"}), 500

# --- TELEGRAM BOT ---
def send_message(text):
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": False},
            timeout=15
        )
        if resp.status_code != 200:
            print(f"Telegram error: {resp.text}")
        else:
            print(f"✅ Sent at {datetime.now()}")
    except Exception as e:
        print(f"Send error: {e}")

def get_reddit_highlights():
    deals = []
    headers = {"User-Agent": "MoneyHunterUKBot/2.0"}
    keywords = ["£", "bonus", "referral", "switch", "free share", "cashback", "offer", "reward"]
    seen = set()
    for endpoint in ["hot", "new"]:
        try:
            r = requests.get(
                f"https://www.reddit.com/r/beermoneyuk/{endpoint}.json?limit=30",
                headers=headers, timeout=15
            )
            if r.status_code != 200:
                continue
            posts = r.json()["data"]["children"]
            for p in posts:
                d = p["data"]
                title, pid = d["title"], d["id"]
                if pid in seen:
                    continue
                if any(kw in title.lower() for kw in keywords):
                    seen.add(pid)
                    link = "https://reddit.com" + d["permalink"]
                    deals.append((title[:70], link, d.get("score", 0)))
        except Exception as e:
            print(f"Reddit error: {e}")
    deals.sort(key=lambda x: x[2], reverse=True)
    return deals[:3]

# --- MESSAGE TEMPLATES ---
def monday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"🏆 *MONEY HUNTERS: WEEKLY KICKOFF* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "🏦 *THIS WEEK'S BEST BANK SWITCHES:*\n\n"
    msg += "🥇 *Lloyds Bank* → *£200*\n"
    msg += "   Open + switch + £2k deposit + 2 DDs\n\n"
    msg += "🥈 *First Direct* → *£175 + 7% saver*\n"
    msg += "   Switch + £1k deposit — best savings rate too\n\n"
    msg += "🥉 *NatWest* → *£150*\n"
    msg += "   Switch + 2 Direct Debits\n\n"
    msg += "💡 *Hunter Tip:* Start Lloyds today — switches take 7 working days, so you could be paid by next week.\n\n"
    msg += f"📱 [Open the app to start tracking]({APP_URL}/app.html)"
    send_message(msg)

def tuesday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"📈 *TUESDAY INVEST BONUSES* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "Quick invest bonuses this week:\n\n"
    msg += "• *Freetrade* → Free share (worth £3–£100)\n"
    msg += "  Deposit just £1 to trigger it\n\n"
    msg += "• *Robinhood UK* → Free share (up to £140)\n"
    msg += "  Deposit £1, hold for 5 days\n\n"
    msg += "• *Webull* → *£50 cash*\n"
    msg += "  Deposit £500, hold 60 days\n\n"
    msg += "💡 Freetrade + Robinhood together = potentially £200 for £2 total deposit.\n\n"
    msg += f"📱 [Track your invest bonuses]({APP_URL}/app.html)"
    send_message(msg)

def wednesday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"🛒 *WEDNESDAY STACKING GUIDE* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "How to save 20%+ on your weekly shop:\n\n"
    msg += "*Step 1* — Buy a supermarket gift card via *Jam Doughnut* (code *8TGF*)\n"
    msg += "   → Tesco 4.5% off · Sainsbury's 4% off · Waitrose 3.8% off\n\n"
    msg += "*Step 2* — Pay for the gift card with a cashback card\n"
    msg += "   → Amex or Chase gives another 1–2% on top\n\n"
    msg += "*Step 3* — Use Clubcard/Nectar prices in store\n"
    msg += "   → Can be another 5–10% off on selected items\n\n"
    msg += "Total saving: *up to 20%+ on your weekly shop*\n\n"
    msg += f"📱 [See full stacking guide]({APP_URL}/app.html)"
    send_message(msg)

def thursday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"💳 *THURSDAY CASHBACK REMINDER* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "Quick check — are you doing these before every online purchase?\n\n"
    msg += "✅ *TopCashback* — check before ANY online shop\n"
    msg += "✅ *Quidco* — compare rates with TopCashback\n"
    msg += "✅ *Jam Doughnut* — gift cards before in-store shops\n"
    msg += "✅ *Airtime Rewards* — Amazon gift cards at 2% off\n\n"
    msg += "💡 If you spent £500 online last month and used cashback, you could have earned £10–£25 back.\n\n"
    msg += f"📱 [Open the cashback section]({APP_URL}/app.html)"
    send_message(msg)

def friday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"💸 *FRIDAY QUICK WINS* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "Under 5 minutes each — grab them this weekend:\n\n"
    msg += "⚡ *Zilch* → £5 instant credit\n"
    msg += "⚡ *Curve* → 1% cashback for 30 days\n"
    msg += "⚡ *Monzo* → £5–£50 random reward (spend £1)\n"
    msg += "⚡ *Revolut* → £20 bonus\n\n"
    msg += "These are all free to open and take minutes. Stack them all.\n\n"
    msg += f"🏹 [Claim your weekend wins]({APP_URL}/app.html)"
    send_message(msg)

def saturday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"📊 *SATURDAY PAYOUT CHECK* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "Take 2 minutes to check your pending payouts:\n\n"
    msg += "🔍 Did any bank switch bonuses land this week?\n"
    msg += "🔍 Any free shares received from Freetrade or Robinhood?\n"
    msg += "🔍 Cashback ready to withdraw on TopCashback or Quidco?\n\n"
    msg += "Mark them as Completed in the app to keep your tracker accurate.\n\n"
    msg += f"📱 [Check your progress]({APP_URL}/app.html)"
    send_message(msg)

def sunday_message():
    today = datetime.now().strftime("%A %d %b")
    msg = f"🗓️ *SUNDAY SETUP* — {today}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "Set yourself up for a profitable week:\n\n"
    msg += "1️⃣ Pick ONE bank switch to start tomorrow\n"
    msg += "   → Lloyds (£200) or First Direct (£175) are best right now\n\n"
    msg += "2️⃣ Check your Jam Doughnut rates for this week's shop\n\n"
    msg += "3️⃣ Review any pending payouts — are they overdue?\n\n"
    msg += "4️⃣ Share the app with one person who'd benefit\n\n"
    msg += f"📱 [Plan your week]({APP_URL}/app.html)"
    send_message(msg)

def daily_digest():
    day = datetime.now().weekday()
    # All days now have proper content — no more blank messages
    if day == 0:   monday_message()
    elif day == 1: tuesday_message()
    elif day == 2: wednesday_message()
    elif day == 3: thursday_message()
    elif day == 4: friday_message()
    elif day == 5: saturday_message()
    else:          sunday_message()

    # Also post a Reddit highlight if available
    try:
        reddit = get_reddit_highlights()
        if reddit:
            msg = "🔥 *HOT ON r/BEERMONEYUK RIGHT NOW:*\n\n"
            for title, link, score in reddit[:2]:
                msg += f"• [{title}]({link}) ↑{score}\n"
            send_message(msg)
    except Exception as e:
        print(f"Reddit digest error: {e}")

def run_scheduler():
    schedule.every().day.at("09:00").do(daily_digest)
    print("🤖 Scheduler active — daily digest at 09:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    send_message(f"🚀 *Money Hunters Bot is live!*\nVisit: {APP_URL}")
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Starting on port {port}")
    app.run(host="0.0.0.0", port=port)
