"""Static offers page generator for Money Hunters UK.

Reads the deal payload the scraper builds (all_deals.json) and writes
offers.html: a plain, crawlable snapshot of today's tracked offers.
Facts only - store, item, amounts and dates come straight from the
scraper; no finance copy is authored here. The interactive board at
app.html remains the source for labelled referral links.

Usable standalone:  python3 scripts/make_offers_page.py
"""
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "all_deals.json"
OUT = ROOT / "offers.html"
SITEMAP = ROOT / "sitemap.xml"
SITE = "https://moneyhunters.co.uk"

GROUP_ORDER = [
    ("bank_switch", "Bank switch bonuses"),
    ("invest", "Invest & pension bonuses"),
    ("cashback", "Cashback & deals"),
    ("utilities", "Utilities & broadband"),
    ("supermarket", "Supermarket prices"),
    ("referral", "Referral offers"),
    ("earn", "Earn & freebies"),
    ("megalist", "More offers"),
]
FALLBACK_GROUPS = [
    ("travel", "Travel"),
    ("business", "Business"),
    ("credit", "Credit"),
    ("transfer", "Transfers"),
    ("freebies", "Freebies"),
    ("pension", "Invest & pension bonuses"),
]


def money_bits(deal):
    out = []
    price = str(deal.get("deal_price") or "")
    was = str(deal.get("original_price") or "")
    saving = deal.get("saving_percent")
    if price:
        out.append(price)
    # only show a "was" line when it is a real previous price, not a zero placeholder
    if was and was not in ("£0", "£0.00", "0", "0.00") and saving and 0 < saving < 100:
        out.append("was {} (-{}%)".format(was, saving))
    return " ".join(out)


def build_html():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    deals = data.get("deals") or []
    checked = data.get("last_updated") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    month = datetime.strptime(checked[:10], "%Y-%m-%d").strftime("%B %Y")
    checked_long = datetime.strptime(checked[:10], "%Y-%m-%d").strftime("%-d %B %Y") if sys.platform != "win32" else checked[:10]

    groups = {}
    for d in deals:
        t = d.get("type") or "megalist"
        if t in ("pension",):
            t = "invest"
        if t == "freebies":
            t = "earn"
        groups.setdefault(t, []).append(d)

    sections = []
    seen_types = set()
    for t, label in GROUP_ORDER + FALLBACK_GROUPS:
        if t in seen_types or t not in groups:
            continue
        seen_types.add(t)
        rows = []
        for d in sorted(groups[t], key=lambda x: str(x.get("store", "")).lower()):
            store = html.escape(str(d.get("store", "")))
            item = html.escape(str(d.get("item", "")))
            amt = html.escape(money_bits(d))
            link = html.escape(str(d.get("link", "")), quote=True)
            updated = html.escape(str(d.get("last_updated") or checked)[:10])
            if not store or not item:
                continue
            amt_html = '<span class="amt">{}</span>'.format(amt) if amt else ""
            rows.append(
                '<div class="offer">'
                "<h3>{} {}</h3>"
                "<p>{} · checked {} · "
                '<a href="{}" rel="nofollow noopener" target="_blank">retailer\'s own page</a>'
                "</p></div>".format(store, amt_html, item, updated, link)
            )
        if rows:
            sections.append("<h2>{} ({})</h2>\n{}".format(html.escape(label), len(rows), "\n".join(rows)))

    page = PAGE.format(
        site=SITE,
        month=html.escape(month),
        checked=html.escape(checked_long),
        n=len(deals),
        sections="\n".join(sections),
    )
    OUT.write_text(page, encoding="utf-8")
    return len(deals)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UK money offers, updated daily ({month}) — Money Hunters UK</title>
<link rel="canonical" href="{site}/offers.html">
<meta name="description" content="Every offer in the Money Hunters UK tracker, rendered fresh from the daily scraper: bank switches, invest bonuses, cashback, utilities and supermarket prices. Conditions apply; each retailer's own page is the source of truth.">
<meta name="theme-color" content="#080b10">
<link rel="icon" type="image/png" href="/icon-192.png">
<style>
:root {{
  --bg: #080b10; --bg2: #0d1219; --g: #1fe887; --t: #f0f4f8; --tm: #8a9bb0; --tl: #4a5d72; --line: rgba(255,255,255,.06);
  --fh: 'Inter', sans-serif; --fb: 'DM Sans', sans-serif;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); font-family: var(--fb); color: var(--t); line-height: 1.7; }}
.wrap {{ max-width: 760px; margin: 0 auto; padding: 48px 24px 64px; }}
h1 {{ font-family: var(--fh); font-size: 30px; font-weight: 800; margin-bottom: 6px; }}
.updated {{ font-size: 13px; color: var(--tl); margin-bottom: 24px; }}
h2 {{ font-family: var(--fh); font-size: 19px; font-weight: 600; color: var(--g); margin: 32px 0 10px; }}
p, li {{ font-size: 15px; color: var(--tm); margin-bottom: 10px; }}
a {{ color: var(--g); }}
.offer {{ background: var(--bg2); border: 1px solid var(--line); border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; }}
.offer h3 {{ font-family: var(--fh); font-size: 16px; font-weight: 600; color: var(--t); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px; }}
.offer h3 .amt {{ color: var(--g); font-weight: 800; }}
.offer p {{ margin: 6px 0 0; font-size: 14px; }}
.cta {{ margin-top: 32px; padding: 16px 20px; background: var(--bg2); border: 1px solid var(--line); border-radius: 12px; }}
</style>
</head>
<body>
<div class="wrap">
<h1>UK money offers ({month})</h1>
<p class="updated">{n} tracked offers · last checked {checked} · moneyhunters.co.uk · free, independent, not financial advice</p>
<p>Amounts are as shown on each retailer's own page when last scraped. Conditions apply and each retailer's page is the source of truth. The labelled referral links live on the full interactive board at app.html; the links here are plain retailer pages.</p>
{sections}
<div class="cta"><p><a href="/app.html">Open the full interactive board →</a> · <a href="/guides/">Read the guides →</a></p></div>
</div>
</body>
</html>
"""


def upsert_sitemap():
    if not SITEMAP.exists():
        return
    text = SITEMAP.read_text(encoding="utf-8")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = (
        "  <url>\n    <loc>{}/offers.html</loc>\n"
        "    <lastmod>{}</lastmod>\n"
        "    <changefreq>daily</changefreq>\n"
        "    <priority>0.9</priority>\n  </url>\n".format(SITE, today)
    )
    if "offers.html" in text:
        text = re.sub(
            r"(<loc>{}/offers\.html</loc>\s*<lastmod>)[^<]*(</lastmod>)".format(re.escape(SITE)),
            r"\g<1>{}\g<2>".format(today),
            text,
        )
    else:
        text = text.replace("</urlset>", entry + "</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    n = build_html()
    upsert_sitemap()
    print("offers.html written with {} deals; sitemap updated".format(n))
