"""Creates data/offer_state.json (one record per provider) from all_deals.json and the app offers dump.

Usage: python3 scripts/seed_offer_state.py app_offers.json
Existing records are kept: only missing providers and missing fields are added, so hand-set values
(max_claim, source_url, conditions) are never overwritten. last_checked / checked_by / status are
written ONLY by the scraper's check step (scripts/offer_autoupdate.py) and this script never sets them
beyond the initial empty values.
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import offer_policy as pol  # noqa: E402
import make_offers_page as mop  # noqa: E402

ROOT = pol.ROOT
INVEST_YES = {"investengine", "lightyear", "freetrade", "robinhood", "webull", "wealthify", "nutmeg", "ajbell", "fidelity",
              "pensionbee", "penfold", "wealthyhood", "trading212", "etoro", "xtb", "igsharedealingaccount"}
CONFIRMED = {"igsharedealingaccount": {"referral_product": "shares", "reward_type": "other", "notes": "Alberto confirmed 21 Nov 2026: referral terms are for a share dealing account (no CFD or spread betting). Label: Share dealing account."}}
INVEST_BORDERLINE = {"plum": "saving and investing app; kept as a saving tool", "moneybox": "saving and investing app",
                     "chip": "savings app with an investing option", "raisin": "savings marketplace",
                     "raisinuk": "savings marketplace", "tembo": "savings and pensions product"}
CRYPTO_RX = re.compile(r"coinbase|kraken|binance|bitpanda|uphold|gemini|crypto|bitcoin|coin\b", re.I)
FCA_OTHER_RX = re.compile(r"bank|barclays|hsbc|natwest|lloyds|halifax|nationwide|first ?direct|chase|monzo|revolut|starling|"
                          r"santander|co-?op|zopa|kroo|klarna|clearpay|zilch|wise|remitly|worldremit|xe\b|worldfirst|currensea|"
                          r"curve|tide|gohenry|rooster|yonder|glint|amex|american express|vitality|mortgage|credit|loan", re.I)


def reward_type(text):
    t = text.lower()
    if re.search(r"share", t): return "shares"
    if re.search(r"gift card|voucher|pass\b|coffee|cake", t): return "other"
    if re.search(r"credit", t): return "credit"
    if re.search(r"£|cash|bonus", t): return "cash"
    return "other"


def main():
    app = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["offers"] if len(sys.argv) > 1 else []
    deals = json.loads((ROOT / "all_deals.json").read_text(encoding="utf-8"))["deals"]
    markers = mop.ref_markers()
    state = pol.load_state()
    seen = {}
    for d in deals:
        k = pol.key(d["store"])
        r = seen.setdefault(k, {"name": d["store"], "texts": [], "src": "", "ref": False, "type": d.get("type"), "premier": ""})
        r["texts"].append(d["item"])
        if mop.is_referral(d, markers): r["ref"] = True
        elif not r["src"]: r["src"] = d.get("link", "")
    for o in app:
        k = pol.key(o["name"])
        r = seen.setdefault(k, {"name": o["name"], "texts": [], "src": "", "ref": False, "type": "", "premier": ""})
        r["texts"] += [str(o.get("reward", "")), o.get("desc", "")]
        if o.get("ref"): r["ref"] = True
        elif o.get("url") and o["url"] != "#" and not r["src"]: r["src"] = o["url"]
        if re.search(r"premier eligib|requires £|£1\d\dk", o.get("desc", ""), re.I) and "premier" in (o["name"] + o["id"]).lower():
            r["premier"] = o["desc"]
    out = state
    for k, r in sorted(seen.items()):
        text = " ".join(r["texts"])
        base = out.get(k, {})
        inv = "yes" if k in INVEST_YES or (r["type"] in ("invest", "pension")) else ("borderline" if k in INVEST_BORDERLINE else "no")
        if k in INVEST_BORDERLINE: inv = "borderline"
        if r["type"] == "invest" and k not in INVEST_YES and k not in INVEST_BORDERLINE: inv = "yes"
        rec = {
            "provider": r["name"],
            "investing": inv,
            "crypto": bool(CRYPTO_RX.search(r["name"])),
            "reward_type": reward_type(text),
            "referral_product": ("shares" if re.search(r"\bshare", text, re.I) and inv != "no" else ("unknown" if inv != "no" else "")),
            "conditions": r["premier"],
            "listing_terms": pol.plain(" | ".join(dict.fromkeys(t for t in r["texts"][:3] if t)))[:300],
            "max_claim": None,
            "source_url": "" if r["ref"] else r["src"],
            "source_is_provider_page": bool(r["src"]) and not r["ref"],
            "last_checked": None,
            "checked_by": None,
            "status": "check",
            "fca_priority": 1 if (inv != "no" or CRYPTO_RX.search(r["name"])) else (2 if FCA_OTHER_RX.search(r["name"]) else 0),
            "hidden": False,
            "hidden_reason": "",
            "notes": INVEST_BORDERLINE.get(k, ""),
        }
        if pol.is_hidden_provider(r["name"]):
            rec["hidden"] = True
            rec["hidden_reason"] = ("referral terms not confirmed as share dealing; hidden until confirmed" if k.startswith("ig")
                                    else "CFD / leveraged broker, not promoted")
        for f, v in rec.items():
            base.setdefault(f, v)
        base.update(CONFIRMED.get(k, {}))
        out[k] = base
    out = {k: out[k] for k in sorted(out)}
    path = pol.STATE_PATH
    path.write_text(json.dumps({"_doc": "One record per provider. last_checked, checked_by and status are written only by the scraper check step; everything else is edited by a person. See scripts/offer_policy.py.", "offers": out}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    from collections import Counter
    print(len(out), "providers", dict(Counter(v["investing"] for v in out.values())))


if __name__ == "__main__":
    main()
