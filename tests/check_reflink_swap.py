"""Referral-link swap must never touch investing/crypto/restricted providers."""
import importlib.util, os, sys
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("scraper", "scraper.py")
sc = importlib.util.module_from_spec(spec); sys.modules["scraper"] = sc; spec.loader.exec_module(sc)
state = sc._offer_state_records()
fail = []
def blocked(o): return sc._swap_blocked(o, state)
for name in ("Freetrade", "Chase UK", "IG (Share dealing account)", "Lightyear", "Webull", "Robinhood UK", "Plum", "Moneybox"):
    if not blocked({"store": name, "link": "https://x.example/ref"}):
        fail.append(f"{name} should be blocked")
if not blocked({"store": "Some Broker", "badge": "INVEST", "link": "https://x.example/ref"}):
    fail.append("invest badge should be blocked")
if blocked({"store": "TopCashback", "badge": "CASHBACK", "category": "cashback", "link": "https://x.example/ref"}):
    fail.append("TopCashback should be allowed")
markers = ["REFX"]
sc._ref_markers = lambda: markers
manual = [{"store": "TopCashback", "link": "https://www.topcashback.co.uk/ref/REFX", "code": "C1"},
          {"store": "Freetrade", "link": "https://freetrade.io/REFX"}]
deals = [{"link": "https://www.topcashback.co.uk/x", "code": ""}, {"link": "https://freetrade.io/free-share", "code": ""}]
out = sc.apply_referral_links([dict(d) for d in deals], manual)
if "REFX" not in out[0]["link"]: fail.append("TopCashback deal should swap")
if "REFX" in out[1]["link"]: fail.append("Freetrade deal must not swap")
print("FAIL: " + "; ".join(fail) if fail else "ok check_reflink_swap")
sys.exit(1 if fail else 0)
