"""Per-offer landing pages for Money Hunters UK (programmatic SEO).

Reads all_deals.json (the scraper's checked snapshot) and writes one static
page per store+type under offers/<slug>/index.html. Facts only: amounts,
conditions text and check dates come straight from the scraper and
data/offer_state.json. No finance copy is authored here: wording, Ad labels
and the disclosure line are reused from scripts/make_offers_page.py, which
Albertino has reviewed.

Run:  python3 scripts/build_offer_pages.py [--limit N]
"""
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import make_offers_page as mop  # noqa: E402  (reviewed wording + labelling)
import offer_policy as pol  # noqa: E402

DATA = ROOT / "all_deals.json"
OUT = ROOT / "offers"
SITE = "https://moneyhunters.co.uk"

# Existing guide pages, one or two per offer type. Paths verified against sitemap.xml.
GUIDES = {
    "bank_switch": ["guides/how-a-cass-switch-works/", "guides/bank-switch-bonuses-the-rules/"],
    "invest": ["guides/investing-basics/", "guides/free-share-offers/"],
    "cashback": ["guides/cashback-sites/", "guides/making-cashback-track/"],
    "utilities": ["guides/energy-bills/", "guides/broadband-and-mobile/"],
    "supermarket": ["guides/supermarket-stacking/", "guides/unit-prices-and-real-value/"],
    "referral": ["guides/referral-programmes/", "guides/cashback-sites/"],
    "earn": ["guides/side-income-and-hmrc/"],
    "megalist": ["guides/stacking-in-the-right-order/"],
    "travel": ["guides/cashback-sites/"],
    "business": ["guides/cashback-sites/"],
    "credit": ["guides/your-credit-score/"],
    "transfer": ["guides/cashback-sites/"],
}
FOOTER = ("Not financial advice. Some links pay us a referral fee and are marked Ad. "
          "Amounts are maximums, conditions apply, and you should verify each one on the provider's page.")


def norm_type(t):
    t = t or "megalist"
    if t in ("pension",):
        t = "invest"
    if t == "freebies":
        t = "earn"
    return t


def amount_text(deal, st, t):
    """Same amount logic make_offers_page.py shows for this deal's row."""
    investing = pol.is_investing(st) or t == "invest"
    if investing:
        a_txt, _ = pol.display_amount(dict(st, investing="yes") if not pol.is_investing(st) else st, "", "")
        return a_txt
    _ov = (st.get("amount_override") or {}).get("value")
    if _ov and not pol.is_investing(st) and t != "invest":
        return str(_ov)
    if pol.is_premier(str(deal.get("store", "")) + " " + str(deal.get("item", ""))):
        a_txt, _ = pol.display_amount(st, deal.get("deal_price"), str(deal.get("store", "")) + " " + str(deal.get("item", "")))
        if a_txt != str(deal.get("deal_price") or ""):
            return a_txt
    return mop.money_bits(deal)


def item_text(deal, st, t):
    investing = pol.is_investing(st) or t == "invest"
    if investing:
        return "Sign-up offer. Conditions, such as a minimum deposit or time limit, are on the provider's page."
    if pol.is_premier(str(deal.get("store", "")) + " " + str(deal.get("item", ""))):
        a_txt, _ = pol.display_amount(st, deal.get("deal_price"), str(deal.get("store", "")) + " " + str(deal.get("item", "")))
        if a_txt != str(deal.get("deal_price") or ""):
            return "Premier account switch. The provider's eligibility conditions are on its own page."
    return html.unescape(mop.plain(str(deal.get("item", ""))))


def link_html(deal, markers, store_label):
    link = html.escape(str(deal.get("link", "")), quote=True)
    if mop.is_referral(deal, markers):
        out = ('<span class="ad">Ad</span> '
               '<a href="{}" rel="sponsored nofollow noopener" target="_blank">referral link</a>'
               " · we may earn a commission".format(link))
        plain_url = mop._provider_sites().get(pol.key(store_label))
        if plain_url:
            out += ' · <a href="{}" rel="nofollow noopener" target="_blank">{}\'s own site (no referral)</a>'.format(
                html.escape(plain_url, quote=True), html.escape(store_label))
        return out
    return '<a href="{}" rel="nofollow noopener" target="_blank">provider\'s own page</a>'.format(link)


def verified_html(deal, st):
    ver = html.escape(pol.verification_label(st))
    if st.get("source_url") and pol.verified_by_fetch(st):
        ver = '<a href="{}" rel="nofollow noopener" target="_blank">{}</a>'.format(
            html.escape(st["source_url"], quote=True), ver)
    return ver


def build_page(store_label, t, rows, checked_long, today, slug):
    """One static page per store+type. rows: list of (deal, st)."""
    st = rows[0][1]
    amt = amount_text(rows[0][0], st, t) or "value varies"
    title = "{} {}: {} · Money Hunters UK".format(store_label, mop.GROUP_ORDER_LABELS.get(t, t), amt) \
        if hasattr(mop, "GROUP_ORDER_LABELS") else "{} offer: {} · Money Hunters UK".format(store_label, amt)
    desc = "{} {} offer. {}. Conditions and the date we last checked it. Part of the Money Hunters UK offers list.".format(
        store_label, mop.GROUP_ORDER_LABELS.get(t, t) if hasattr(mop, "GROUP_ORDER_LABELS") else "", amt)
    risk = ""
    if t == "invest":
        risk = '<p class="risk"><strong>Risk warning:</strong> {}</p>'.format(html.escape(mop.RISK_WARNING))
    item_rows = []
    for deal, _st in rows:
        mk = link_html(deal, ROWS["markers"], store_label)
        item_rows.append(
            '<li><strong>{}</strong> {}<br>{}<br><small>{}</small><br>{}</li>'.format(
                html.escape(item_text(deal, _st, t)),
                ('<span class="amt">{}</span>'.format(html.escape(amount_text(deal, _st, t)))
                 if amount_text(deal, _st, t) else ""),
                mk,
                html.escape(mop.verify_text(deal, checked_long)),
                verified_html(deal, _st),
            ))
    guide_links = "".join('<li><a href="/{}">{}</a></li>'.format(
        g, {"guides/how-a-cass-switch-works/": "How a CASS switch works",
            "guides/bank-switch-bonuses-the-rules/": "Bank switch bonuses: the rules",
            "guides/investing-basics/": "Investing basics",
            "guides/free-share-offers/": "Free share offers",
            "guides/cashback-sites/": "Cashback sites",
            "guides/making-cashback-track/": "Making cashback track",
            "guides/energy-bills/": "Energy bills",
            "guides/broadband-and-mobile/": "Broadband and mobile",
            "guides/supermarket-stacking/": "Supermarket stacking",
            "guides/unit-prices-and-real-value/": "Unit prices and real value",
            "guides/referral-programmes/": "Referral programmes",
            "guides/side-income-and-hmrc/": "Side income and HMRC",
            "guides/stacking-in-the-right-order/": "Stacking in the right order",
            "guides/your-credit-score/": "Your credit score"}.get(g, g)) for g in GUIDES.get(t, []))
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": "{}/offers/{}/".format(SITE, slug),
        "dateModified": today,
        "isPartOf": {"@type": "WebSite", "name": "Money Hunters UK", "url": SITE + "/"},
    }, ensure_ascii=False)
    page = """<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}/offers/{slug}/">
<script type="application/ld+json">{jsonld}</script>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:640px;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#1a1a1a}}
a{{color:#0a6e6e}}.ad{{background:#fff3d6;border:1px solid #e0c26a;border-radius:3px;padding:0 .3em;font-size:.85em}}
.amt{{color:#0a6e6e;font-weight:600}}.risk{{color:#7a4b00;background:#fff8ec;border:1px solid #e6d2a8;border-radius:4px;padding:.6rem .8rem}}
footer{{color:#555;font-size:.9em;border-top:1px solid #ddd;margin-top:2rem;padding-top:1rem}}
</style>
</head>
<body>
<p><a href="/">Money Hunters UK</a> · <a href="/app.html?view=offers">All offers in the app</a> · <a href="/offers.html">Full list</a></p>
<h1>{h1}</h1>
<p><small>{verify0}</small></p>
{risk}
<h2>What you have to do</h2>
<ul>
{rows}
</ul>
<h2>Read more</h2>
<ul>
{guides}
</ul>
<p>Check how the numbers work out for you in the <a href="/app.html">worth-my-time calculator</a> in the app, and see every tracked offer in the <a href="/app.html?view=offers">offers list</a>.</p>
<footer>{footer}<br>Page facts come from the daily scrape, checked {today}.</footer>
</body>
</html>""".format(
        title=html.escape(title), desc=html.escape(desc), site=SITE, slug=slug,
        jsonld=jsonld.replace("</", "<\\/"),
        h1=html.escape("{} {}".format(store_label, amt)),
        verify0="Checked {} via the daily scrape.".format(checked_long),
        risk=risk, rows="\n".join(item_rows), guides=guide_links, footer=FOOTER, today=checked_long)
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page, encoding="utf-8")
    return slug


ROWS = {"markers": []}
mop.GROUP_ORDER_LABELS = dict(mop.GROUP_ORDER + mop.FALLBACK_GROUPS)


def main():
    ROWS["markers"] = mop.ref_markers()
    if not ROWS["markers"]:
        raise SystemExit("REF_MARKERS not found in app.html: refusing to build unlabelled pages")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    deals = data.get("deals") or []
    checked = data.get("last_updated") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    checked_long = datetime.strptime(checked[:10], "%Y-%m-%d").strftime("%-d %B %Y") if sys.platform != "win32" else checked[:10]
    today = checked[:10]
    groups = {}
    seen_rows = set()
    for d in deals:
        if mop.is_hidden(d):
            continue
        dk = (mop.store_key(d), str(d.get("deal_price") or "").strip().lower(), d.get("type"))
        if dk in seen_rows:
            continue
        seen_rows.add(dk)
        t = norm_type(d.get("type"))
        if pol.state_for(mop.STATE, d.get("store")).get("status") == "ended":
            continue  # no landing page for ended offers
        groups.setdefault((mop.store_key(d), t), []).append(d)
    slugs = {}
    for (sk, t), ds in groups.items():
        store_label = html.unescape(str(ds[0].get("store", "")))
        ds.sort(key=lambda x: (str(x.get("last_verified") or ""), str(x.get("deal_price") or "")), reverse=True)
        base = mop._slug("{} {}".format(store_label, t))
        slug, n = base, 2
        while slug in slugs:
            slug = "{}-{}".format(base, n)
            n += 1
        slugs[slug] = build_page(store_label, t, [(d, pol.state_for(mop.STATE, d.get("store"))) for d in ds], checked_long, today, slug)
    print("wrote {} offer pages to offers/".format(len(slugs)))
    (ROOT / "offers" / "index.json").write_text(json.dumps({"checked": today, "pages": sorted(slugs)}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
