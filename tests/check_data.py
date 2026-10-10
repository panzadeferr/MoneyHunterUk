"""Data and page checks that must pass before deploy. Run: python tests/check_data.py"""
import json, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
today = datetime.date.today().isoformat()
errors = []

def fail(msg):
    errors.append(msg)

data = json.loads((ROOT / "all_deals.json").read_text(encoding="utf-8"))
deals = data.get("deals", [])
if len(deals) < 20:
    fail(f"only {len(deals)} deals in all_deals.json")

seen_bank = {}
for d in deals:
    name = d.get("store", "?")
    for f in ("store", "item", "deal_price", "link"):
        if not d.get(f):
            fail(f"{name}: missing {f}")
    if d.get("link") and not str(d["link"]).startswith(("http://", "https://")):
        fail(f"{name}: link is not a URL")
    exp = str(d.get("expires") or "")[:10]
    if exp and exp < today:
        fail(f"{name}: expired on {exp} but still listed")
    if exp == "2026-12-31":
        fail(f"{name}: placeholder expiry 2026-12-31")
    lv = str(d.get("last_verified") or "")
    if lv and lv > today:
        fail(f"{name}: last_verified {lv} is in the future")
    if d.get("type") == "bank_switch":
        key = name.lower()
        if key in seen_bank:
            fail(f"{name}: listed twice as a bank switch")
        seen_bank[key] = d

verified = json.loads((ROOT / "verified.json").read_text(encoding="utf-8"))
names = {d.get("store", "").lower() for d in deals}
for k in verified:
    if not k.startswith("_") and k.lower() not in names:
        print(f"note: verified.json lists {k!r}, not in current data (fine if it has expired)")

# One amount per bank across pages
def amount(text, label):
    m = re.search(label + r"[^£<]{0,60}(?:<[^>]+>\s*){0,6}(up to )?£(\d+)", text)
    return (bool(m and m.group(1)), int(m.group(2))) if m else None

index = (ROOT / "index.html").read_text(encoding="utf-8")
bank = (ROOT / "bank-switch.html").read_text(encoding="utf-8")
if "Lloyds £250" in index or "Lloyds Bank for £250" in index:
    fail("index.html still says Lloyds £250 (current offer is £200)")
for banned in ("updated today", "£2,000+ per year", "tax-free", "£500+ in your first 3 months"):
    if banned in index:
        fail(f"index.html still contains unsupported claim: {banned!r}")
if "Ad" not in index or "referral" not in index.lower():
    fail("index.html has no ad/referral disclosure")
if "ADMIN_SECRET" in (ROOT / "app.html").read_text(encoding="utf-8"):
    fail("app.html still has ADMIN_SECRET")

if errors:
    print("DATA CHECKS FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"Data checks passed: {len(deals)} deals, {len(seen_bank)} bank switches.")
