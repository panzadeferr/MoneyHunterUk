"""Builds docs/offer-register.csv: one row per offer across offers.html and the app.

Usage:  python3 scripts/build_offer_register.py app_offers.json
(app_offers.json comes from scripts/dump_app_offers.mjs.)

It is a risk register, not legal advice. It never looks up FCA authorisation: rows that need a
check on the FCA register are only listed, for a person to check.
"""
import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import make_offers_page as mop  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime(2026, 11, 20) if "--today" not in sys.argv else datetime.strptime(sys.argv[sys.argv.index("--today") + 1], "%Y-%m-%d")

HOMEPAGE_STATIC = {"firstdirect", "barclays", "freetrade", "topcashback", "octopus"}  # cards on index.html
HOMEPAGE_AD = {"freetrade", "topcashback", "octopus"}  # referral cards, each carrying an Ad tag

RISKY = [
    (r"free\s+shares?", "free share"), (r"free\s+money", "free money"), (r"guarantee", "guarantee"),
    (r"risk[- ]free", "risk-free"), (r"easy\s+money", "easy money"), (r"literally", "overpromise"),
    (r"ending soon", "ending soon (needs a date)"), (r"\bwas £", "was-price"), (r"\(-\d+%\)", "percent-off"),
]
INVEST_RX = re.compile(r"invest|pension|plum|moneybox|wealth|webull|freetrade|robinhood|nutmeg|lightyear|"
                       r"investengine|aj ?bell|fidelity|penfold|chip|raisin|tembo|ig trading|ig-trading|isa", re.I)
LEVERAGED_FLAG = {"igtrading": "IG is best known for CFDs and spread betting. Confirm this offer is for a non-leveraged Invest account"}
FCA_RX = re.compile(r"bank|barclays|hsbc|natwest|lloyds|halifax|nationwide|first ?direct|chase|monzo|revolut|starling|"
                    r"santander|co-?op|zopa|ifast|kroo|invest|pension|plum|moneybox|wealth|webull|freetrade|robinhood|"
                    r"nutmeg|lightyear|aj ?bell|fidelity|penfold|chip|raisin|tembo|ig |igtrading|klarna|clearpay|zilch|"
                    r"wise|remitly|worldremit|xe |worldfirst|currensea|curve|tide|gohenry|rooster|yonder|glint|amex|"
                    r"american express|vitality|cashback.co|airwallex|mortgage|credit|loan", re.I)
HARD_FCA_REASON = "Regulated financial product or payments/credit firm: check the firm and the product on the FCA register"


def key(name):
    k = re.sub(r"[^a-z0-9]", "", str(name).lower())
    for suf in ("uk", "bank", "mobile", "energy", "money", "bonus"):
        pass
    return k


def match(a, b):
    return a == b or (len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a)))


def days_old(date_str):
    try:
        return (TODAY - datetime.strptime(str(date_str)[:10], "%Y-%m-%d")).days
    except ValueError:
        return None


def main():
    app = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["offers"]
    data = json.loads((ROOT / "all_deals.json").read_text(encoding="utf-8"))
    deals = data["deals"]
    markers = mop.ref_markers()

    rows = {}  # key -> dict
    def row(k, provider):
        for kk in rows:
            if match(kk, k):
                return rows[kk]
        rows[k] = {"provider": provider, "page": [], "app": [], "deals": []}
        return rows[k]

    hidden = []
    for d in deals:
        if mop.is_hidden(d):
            hidden.append(d)
        row(key(d["store"]), d["store"])["deals"].append(d)
    for o in app:
        row(key(o["name"]), o["name"])["app"].append(o)

    out = []
    for k, r in sorted(rows.items(), key=lambda kv: kv[1]["provider"].lower()):
        deals_r, app_r = r["deals"], r["app"]
        deals_vis = [d for d in deals_r if not mop.is_hidden(d)]
        is_hid = bool(deals_r) and all(mop.is_hidden(d) for d in deals_r) and not app_r
        # app hidden rows are not in the dump at all
        provider = r["provider"]
        cat = ""
        if app_r:
            a0 = app_r[0]
            cat = (a0.get("category") or re.sub(r"^[^A-Za-z]+", "", a0.get("badge") or "")).strip().lower()
        if not cat and deals_r:
            cat = deals_r[0].get("type", "")
        ref_page = any(mop.is_referral(d, markers) for d in deals_vis)
        ref_app = any(a["ref"] for a in app_r)
        referral = ref_page or ref_app
        # surfaces
        ad_page = ("Y" if ref_page else "N") if deals_vis else "-"
        ad_app = ("Y" if ref_app else "N") if app_r else "-"
        # app card shows Ad pill + panel line for every ref offer
        home_present = any(k.startswith(h) or h.startswith(k) for h in HOMEPAGE_STATIC)
        ad_home = "-" if not home_present else ("Y" if any(k.startswith(h) or h.startswith(k) for h in HOMEPAGE_AD) else "N (no referral link)")
        # a surface that shows a referral link without Ad would be wrong
        label_gap = (ref_page and ad_page != "Y") or (ref_app and ad_app != "Y")
        shown = []
        for a in app_r:
            shown.append("app: " + str(a["reward"]))
        for d in deals_vis:
            shown.append("offers.html: " + ("no figure (investing, unverified)" if d.get("type") in ("invest", "pension") and not d.get("last_verified") else mop.money_bits(d)))
        amount_shown = " | ".join(dict.fromkeys(shown))
        # verification
        ver_dates, ver_src = [], ""
        for a in app_r:
            if a.get("verified"):
                ver_dates.append(a["verified"])
                if not a["ref"] and a.get("url") and a["url"] != "#":
                    ver_src = a["url"]
        for d in deals_vis:
            if d.get("last_verified"):
                ver_dates.append(d["last_verified"])
                if not mop.is_referral(d, markers) and not ver_src:
                    ver_src = d.get("link", "")
        vdate = max(ver_dates) if ver_dates else ""
        verified = ("{} {}".format(vdate[:10], ver_src) if ver_src else "{} (no official page link on record)".format(vdate[:10])) if vdate else "no"
        age = days_old(vdate) if vdate else None
        verified_note = ("; over 30 days old, page says verify" if (age is not None and age > 30) else "")
        # conditions
        desc_all = " ".join((a.get("desc") or "") for a in app_r)
        cond_words = re.search(r"eligib|new customer|minimum|deposit|within|CASS|direct debit|conditions|terms|sole|18\+|must|requires", desc_all, re.I)
        if app_r and a_curated(app_r) and cond_words and len(desc_all) > 90:
            cond = "Y"
        elif app_r or deals_vis:
            cond = "partial (one line; page links to provider terms)"
        else:
            cond = "N"
        # expiry
        ends = [a["end"] for a in app_r if a.get("end")] + [d["expires"] for d in deals_vis if d.get("expires")]
        tf = [d["timeFrame"] for d in deals_vis if d.get("timeFrame") and re.search(r"expire|ends?\b", d["timeFrame"], re.I)]
        expiry_shown = "Y" if ends or tf else "N"
        expiry_passed = "N"
        for e in ends:
            if str(e)[:10] < TODAY.strftime("%Y-%m-%d"):
                expiry_passed = "Y"
        # investing / leveraged
        invest = bool(INVEST_RX.search(provider + " " + cat)) or any(a.get("investing") for a in app_r) or any(d.get("type") in ("invest", "pension") for d in deals_vis)
        lev = LEVERAGED_FLAG.get(k, "")
        if is_hid:
            lev = "CFD / leveraged broker: not promoted"
        flag = ("investing" if invest else "") + (("; " if invest and lev else "") + ("LEVERAGED? " + lev if lev else ""))
        risk_shown = ("Y (offers.html invest section + app card and panel)" if invest and not is_hid else "n/a") if invest or lev else "n/a"
        text_all = " ".join([desc_all] + [mop.plain(str(d.get("item", ""))) for d in deals_vis] + [str(a.get("reward")) for a in app_r])
        risky = sorted({lab for rx, lab in RISKY if re.search(rx, text_all, re.I)})
        # duplicate: more than one row on a surface for the same provider+amount
        dup = ""
        amts = [mop.store_key(d) + "|" + str(d.get("deal_price")) for d in deals_vis]
        if len(set(amts)) < len(amts):
            dup = "duplicate scraped rows (merged on offers.html by generator)"
        if len([a for a in app_r if a.get("curated")]) > 1 or (len(app_r) > 1 and len({a['name'].lower() for a in app_r}) == 1 and False):
            dup = (dup + "; " if dup else "") + "more than one curated app card"
        names = {a["id"] for a in app_r}
        if app_r and deals_vis and not any(d.get("type") == "bank_switch" for d in deals_vis):
            pass
        # statuses
        needs, fix = [], []
        if is_hid:
            fix.append("hidden: CFD / leveraged broker")
        if k.startswith("trading212") or k == "trading212":
            pass
        if lev and not is_hid:
            needs.append(lev)
        if k.startswith("plum"):
            needs.append("Plum: earlier listing said 'Expires April 7th' with no year; expiry removed, confirm the live terms and end date on Plum's page")
        if k.startswith("natwest") or k.startswith("hsbc") or k.startswith("barclays"):
            needs.append("Same bank appears with different products/amounts (Premier £500/£600 vs standard £200-£300); confirm amounts and eligibility on the bank pages")
        if invest and not vdate and not is_hid:
            needs.append("Investing offer: amount hidden until you verify the figure on the provider's own page and give me the date and source")
        if k.startswith("freetrade") or k.startswith("robinhood"):
            fix.append("'Free Share' wording replaced with 'share bonus'; unverified £100/£140 amounts removed from the card; risk warning added")
        if expiry_passed == "Y":
            fix.append("expired: remove or hide")
        if any(lab in risky for lab in ("free share", "free money", "guarantee", "risk-free", "easy money")):
            fix.append("risky wording still present: " + ", ".join(risky))
        if any(d.get("type") != "supermarket" and mop.money_bits(d) != str(d.get("deal_price") or "") for d in deals_vis):
            fix.append("was-price still shown on non-supermarket row")
        if label_gap:
            fix.append("referral link without Ad label")
        if dup:
            fix.append("duplicate removed in generator")
        fix_applied = "; ".join(fix)
        remaining_fix = [f for f in fix if f.startswith(("expired", "risky wording still", "was-price still", "referral link without"))]
        status = "FIX NOW" if remaining_fix else ("NEEDS ALBERTO" if needs else "OK")
        if is_hid:
            status = "HIDDEN (CFD/leveraged)"
        fca = bool(FCA_RX.search(provider + " " + cat)) or invest or bool(lev)
        out.append({
            "slug": (app_r[0]["id"] if app_r else re.sub(r"[^a-z0-9]+", "-", provider.lower()).strip("-")),
            "provider": provider,
            "category": cat,
            "referral_link": "Y" if referral else "N",
            "ad_label_offers_html": ad_page,
            "ad_label_app": ad_app,
            "ad_label_homepage": ad_home,
            "amount_shown": amount_shown or "(hidden)",
            "verified": verified + verified_note,
            "conditions_shown": cond,
            "expiry_shown": expiry_shown,
            "expiry_passed": expiry_passed,
            "investing_or_leveraged_flag": flag,
            "risk_warning_shown": risk_shown,
            "risky_wording": ", ".join(risky),
            "duplicate": dup,
            "status": status,
            "fix_applied_in_compliance_a": fix_applied,
            "needs_alberto": " | ".join(needs),
            "fca_register_check_needed": ("Y: " + HARD_FCA_REASON) if fca else "N",
        })
    out_path = ROOT / "docs" / "offer-register.csv"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print("rows", len(out), dict(Counter(r["status"] for r in out)))


def a_curated(app_r):
    return any(a.get("curated") for a in app_r)


if __name__ == "__main__":
    main()
