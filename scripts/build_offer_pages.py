"""Per-offer landing pages for Money Hunters UK (programmatic SEO).

Builds one static page per store+type under offers/<slug>/index.html from
all_deals.json and data/offer_state.json.

A page is generated ONLY when the offer either
  a) carries our referral link (mop.is_referral), or
  b) has verified conditions in offer_state.json (conditions plus a
     last_checked date and a source_url).
Everything else gets no page at all. A page whose offer has no verified
date shows "Not yet verified by us", carries
<meta name="robots" content="noindex"> and is left out of the sitemap.

Skip list (never generate, whatever the data says):
- Freetrade: its referral programme terms say the referral link must not be
  shared on public social media or forums. Albertino is waiting on written
  confirmation before we promote it anywhere public. Revisit when he says so.
- trading.com: no page without Albertino's written compliance approval.

Facts only: amounts, conditions text and check dates come from the scraper
and offer_state.json. No finance copy is authored here: wording, Ad labels,
disclosure lines and the amount policy are reused from
scripts/make_offers_page.py and scripts/offer_policy.py (reviewed).
The one-line intro per offer type is process description, not a claim, and
goes through Albertino's review with this PR.

Run:  python3 scripts/build_offer_pages.py
"""
import html
import json
import re
import shutil
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
UMAMI_HTML = (
    '<script>try{var q=new URLSearchParams(location.search).get(\'mh_me\');'
    'if(q===\'1\')localStorage.setItem(\'umami.disabled\',\'1\');'
    'else if(q===\'0\')localStorage.removeItem(\'umami.disabled\')}catch(e){}</script>'
    '<script defer src="https://cloud.umami.is/script.js" '
    'data-website-id="f9d2c068-643f-4cfc-847e-c22fec24bafe"></script>'
    '<script>window.mhTrack=function(n,d){try{if(window.umami&&umami.track)umami.track(n,d)}catch(e){}}</script>'
)
CLICK_JS = (
    '<script>document.querySelectorAll(\'a[data-offer]\').forEach(function(a){'
    'a.addEventListener(\'click\',function(){if(window.mhTrack)mhTrack(\'offer-click\','
    '{offer:a.getAttribute(\'data-offer\')})})});</script>'
)

# Slugs we never build a page for (see the module docstring for why).
SKIP_SLUGS = {"rakuten", "freetrade", "trading", "tradingcom", "trading-com", "tradingdotcom"}

GUIDES = {
    "bank_switch": [("guides/how-a-cass-switch-works/", "How a CASS switch works"),
                    ("guides/bank-switch-bonuses-the-rules/", "Bank switch bonuses: the rules")],
    "invest": [("guides/investing-basics/", "Investing basics"),
               ("guides/free-share-offers/", "Share offers")],
    "cashback": [("guides/cashback-sites/", "Cashback sites"),
                 ("guides/making-cashback-track/", "Making cashback track")],
    "utilities": [("guides/energy-bills/", "Energy bills"),
                  ("guides/broadband-and-mobile/", "Broadband and mobile")],
    "supermarket": [("guides/supermarket-stacking/", "Supermarket stacking"),
                    ("guides/unit-prices-and-real-value/", "Unit prices and real value")],
    "referral": [("guides/referral-programmes/", "Referral programmes"),
                 ("guides/cashback-sites/", "Cashback sites")],
    "earn": [("guides/side-income-and-hmrc/", "Side income and HMRC")],
    "megalist": [("guides/stacking-in-the-right-order/", "Stacking in the right order")],
    "travel": [("guides/cashback-sites/", "Cashback sites")],
    "business": [("guides/cashback-sites/", "Cashback sites")],
    "credit": [("guides/your-credit-score/", "Your credit score")],
    "transfer": [("guides/cashback-sites/", "Cashback sites")],
}

# One short factual intro per offer type: what the offer type is and what to
# check. No amounts promised, no "free", no typical-results claims.
INTROS = {
    "bank_switch": "Bank switch bonuses pay after your old current account moves to the new bank through the "
                   "Current Account Switch Service. Each bank sets its own conditions, such as Direct Debits to "
                   "move or a minimum pay-in. Check them before you start: a switch takes a week or more and "
                   "closes your old account.",
    "invest": "These are sign-up offers from investment and savings apps. Each provider sets its own conditions, "
              "such as a minimum deposit or a holding period, on its own page. Nothing here is advice or a "
              "personal recommendation.",
    "cashback": "Cashback sites pay back a share of what you spend at their partner retailers. Payouts track "
                "after the purchase and can be delayed or rejected, so read the site's own terms first.",
    "utilities": "Energy and mobile providers sometimes pay a bill credit or bonus when you switch to them or "
                 "refer someone. The conditions come from the provider's own pages, with the date we checked.",
    "supermarket": "Supermarket prices move daily. We list what the daily scrape found, with its check date, "
                   "but confirm the price at the shop before you buy.",
    "referral": "Referral offers pay when someone signs up through a link and meets the provider's conditions. "
                "Usually both sides have to complete a step. Read the conditions before you share or use a link.",
    "earn": "These offers pay small amounts for sign-ups or simple tasks. They are rarely worth much per hour; "
            "the worth-my-time calculator in the app helps you check before you spend time on one.",
    "megalist": "Offers we track that do not fit the other groups. Each one lists its conditions and the date we "
                "last checked it.",
    "travel": "Travel offers with conditions shown. Confirm the details on the provider's own page before you book.",
    "business": "Business account offers. Conditions, such as a minimum spend, are on the provider's own page.",
    "credit": "Credit and card offers. Applying usually involves a credit check. Check the provider's own page "
              "for the full terms.",
    "transfer": "Money transfer offers. Conditions, such as a first transfer amount, are on the provider's page.",
}
FALLBACK_INTRO = "Each offer lists its conditions and the date we last checked it. Verify every offer on the provider's own page before you apply."

TYPE_LABELS = {
    "bank_switch": "bank switch bonus", "invest": "sign-up offer", "cashback": "cashback offer",
    "utilities": "switch offer", "supermarket": "offer", "referral": "referral offer",
    "earn": "offer", "megalist": "offer", "travel": "travel offer",
    "business": "business account offer", "credit": "credit offer", "transfer": "transfer offer",
}

FOOTER = ("Not financial advice. Some links pay us a referral fee and are marked Ad. "
          "Amounts are maximums, conditions apply, and you should verify each one on the provider's page.")

# Display-only scrub of wording we never use (mirrors make_offers_page.py's
# _WORDING, plus a bare "free", which the reviewed list also excludes).
_WORDING = [
    (re.compile(r"\bfree\s+shares?\b", re.I), "share bonus"),
    (re.compile(r"\bfree\s+money\b", re.I), "bonus"),
    (re.compile(r"\bguaranteed\b", re.I), "possible"),
    (re.compile(r"\brisk[- ]free\b", re.I), "lower-risk"),
    (re.compile(r"\beasy\s+money\b", re.I), "bonus"),
    (re.compile(r"\bfree\b", re.I), ""),
]


def display_text(text):
    out = mop.plain(str(text or ""))
    for rx, repl in _WORDING:
        out = rx.sub(repl, out)
    return re.sub(r"\s{2,}", " ", out.replace("  ", " ")).strip(" -→")


def amount_text(deal, st, t):
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
    if pol.is_investing(st) or t == "invest":
        return "Sign-up offer. Conditions, such as a minimum deposit or time limit, are on the provider's page."
    if pol.is_premier(str(deal.get("store", "")) + " " + str(deal.get("item", ""))):
        a_txt, _ = pol.display_amount(st, deal.get("deal_price"), str(deal.get("store", "")) + " " + str(deal.get("item", "")))
        if a_txt != str(deal.get("deal_price") or ""):
            return "Premier account switch. The provider's eligibility conditions are on its own page."
    return display_text(deal.get("item", ""))


def dedupe_amount(amt, text):
    """Don't repeat the amount next to text that already shows it."""
    if not amt:
        return ""
    a = re.sub(r"[\s£,]", "", amt.lower())
    b = re.sub(r"[\s£,]", "", str(text).lower())
    return "" if a and a in b else amt


def check_line(st):
    """The offer's own verified date from offer_state.json, labelled with who checked it."""
    lc = str(st.get("last_checked") or "")[:10]
    try:
        human = datetime.strptime(lc, "%Y-%m-%d").strftime("%-d %B %Y") if sys.platform != "win32" else lc
    except ValueError:
        human = ""
    src = st.get("source_url") or ""
    if lc and st.get("checked_by") == "fetch" and src:
        return ('Checked {} by our automated check of '
                '<a href="{}" rel="nofollow noopener" target="_blank">the provider\'s page</a>.').format(human, html.escape(src, quote=True))
    if lc:
        if src:
            return ('Checked {} on <a href="{}" rel="nofollow noopener" target="_blank">the provider\'s page</a>.').format(human, html.escape(src, quote=True))
        return "Checked {} on the provider's page.".format(human)
    return "Not yet verified by us: confirm on the provider's page."


def link_html(deal, markers, store_label, slug):
    """Referral link with the Ad label, or the provider's own page. Codes are
    never shown: the code field stays in the app only."""
    link = html.escape(str(deal.get("link", "")), quote=True)
    if mop.is_referral(deal, markers):
        out = ('<span class="tag">Ad</span> '
               '<a href="{}" data-offer="{}" rel="sponsored nofollow noopener" target="_blank">referral link</a>'
               " · we may earn a commission".format(link, html.escape(slug, quote=True)))
        plain_url = mop._provider_sites().get(pol.key(store_label))
        if plain_url:
            out += ' · <a href="{}" rel="nofollow noopener" target="_blank">{}\'s own site (no referral)</a>'.format(
                html.escape(plain_url, quote=True), html.escape(store_label))
        return out
    return '<a href="{}" rel="nofollow noopener" target="_blank">provider\'s own page</a>'.format(link)


STYLE = """:root {
  --bg: #080b10; --bg2: #0d1219; --bg3: #131b26;
  --g: #1fe887; --gl: rgba(31,232,135,.12);
  --a: #ffcf5a; --al: rgba(255,207,90,.1);
  --t: #f0f4f8; --tm: #8a9bb0; --tl: #4a5d72;
  --line: rgba(255,255,255,.06);
  --fh: 'Inter', sans-serif; --fb: 'DM Sans', sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); font-family: var(--fb); color: var(--t); line-height: 1.7; }
.wrap { max-width: 760px; margin: 0 auto; padding: 32px 24px 64px; }
header { border-bottom: 1px solid var(--line); margin-bottom: 28px; }
header .wrap { padding: 18px 24px; display: flex; gap: 18px; flex-wrap: wrap; align-items: baseline; }
header .brand { font-family: var(--fh); font-weight: 800; color: var(--t); text-decoration: none; }
header nav a { color: var(--tm); text-decoration: none; font-size: 14px; }
header nav a:hover { color: var(--g); }
h1 { font-family: var(--fh); font-size: 28px; font-weight: 800; margin-bottom: 6px; }
h2 { font-family: var(--fh); font-size: 18px; font-weight: 600; color: var(--g); margin: 28px 0 10px; }
p, li { font-size: 15px; color: var(--tm); margin-bottom: 10px; }
strong { color: var(--t); }
a { color: var(--g); }
.checked { font-size: 13px; color: var(--tl); margin-bottom: 20px; }
.offer { background: var(--bg2); border: 1px solid var(--line); border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; }
.offer h3 { font-family: var(--fh); font-size: 16px; font-weight: 600; color: var(--t); }
.offer h3 .amt { color: var(--g); font-weight: 800; }
.offer p { margin: 6px 0 0; font-size: 14px; }
.tag { display: inline-block; font-size: 11px; letter-spacing: .04em; text-transform: uppercase; color: var(--a); margin-right: 6px; }
.risk { color: var(--a); background: var(--al); border: 1px solid rgba(255,207,90,.35); border-radius: 8px; padding: 10px 14px; font-size: 14px; }
footer { color: var(--tl); font-size: 13px; border-top: 1px solid var(--line); margin-top: 32px; padding-top: 16px; }
"""


def build_page(store_label, t, rows, today, slug, markers):
    """rows: list of (deal, st). One page per store+type."""
    st = rows[0][1]
    amt = amount_text(rows[0][0], st, t)
    label = TYPE_LABELS.get(t, "offer")
    verified = bool(st.get("last_checked"))
    h1 = "{} {}".format(store_label, label)
    if amt and "value varies" not in amt and len(amt) <= 18:
        h1 += ": " + amt
    title = "{} · Money Hunters UK".format(h1)
    desc = "{}. Conditions and the date we last checked it. Part of the Money Hunters UK offers list.".format(h1)
    risk = ""
    if t == "invest":
        risk = '<p class="risk"><strong>Risk warning:</strong> {}</p>'.format(html.escape(mop.RISK_WARNING))
    conds = ""
    if str(st.get("conditions") or "").strip():
        conds = ('<h2>Conditions</h2><p>{}</p>').format(html.escape(display_text(st["conditions"])))
    item_rows = []
    for deal, dst in rows:
        it = item_text(deal, dst, t)
        row_amt = dedupe_amount(amount_text(deal, dst, t), it)
        item_rows.append(
            '<div class="offer"><h3>{}{}</h3><p>{}</p><p>{}</p></div>'.format(
                html.escape(it),
                ' <span class="amt">{}</span>'.format(html.escape(row_amt)) if row_amt else "",
                link_html(deal, markers, store_label, slug),
                "" if dst is st or not str(dst.get("conditions") or "").strip() else
                html.escape(display_text(dst["conditions"]))[:0],  # provider-level conditions shown once above
            ))
    rows_html = "\n".join(item_rows)
    guides = "".join('<li><a href="/{}">{}</a></li>'.format(g, lab) for g, lab in GUIDES.get(t, []))
    intro = INTROS.get(t, FALLBACK_INTRO)
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
{noindex}<link rel="canonical" href="{site}/offers/{slug}/">
<script type="application/ld+json">{jsonld}</script>
{umami}
<style>{style}</style>
</head>
<body>
<header><div class="wrap"><a class="brand" href="/">Money Hunters UK</a>
<nav><a href="/app.html?view=offers">All offers</a> <a href="/bank-switch.html">Bank switches</a> <a href="/guides/">Guides</a> <a href="/play/">Play</a> <a href="/newsletter.html">Newsletter</a></nav></div></header>
<div class="wrap">
<h1>{h1}</h1>
<p class="checked">{checked}</p>
{risk}
<p>{intro}</p>
{conds}
<h2>The offer{multi}</h2>
{rows}
<h2>Read more</h2>
<ul>
{guides}
</ul>
<p>Check how the numbers work out for you in the <a href="/app.html">worth-my-time calculator</a> in the app, and see every tracked offer in the <a href="/app.html?view=offers">offers list</a>.</p>
<footer>{footer}<br>Offer facts come from the provider's own pages and the daily scrape. Page generated {today}.</footer>
</div>
{clickjs}
</body>
</html>""".format(
        title=html.escape(title), desc=html.escape(desc), site=SITE, slug=slug,
        noindex='<meta name="robots" content="noindex">\n' if not verified else "",
        jsonld=jsonld.replace("</", "<\\/"), umami=UMAMI_HTML, style=STYLE,
        h1=html.escape(h1), checked=check_line(st), risk=risk, intro=html.escape(intro),
        conds=conds, multi="s" if len(rows) > 1 else "", rows=rows_html,
        guides=guides, footer=FOOTER, today=today, clickjs=CLICK_JS)
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page, encoding="utf-8")
    return slug


def norm_type(t):
    t = t or "megalist"
    if t == "pension":
        t = "invest"
    if t == "freebies":
        t = "earn"
    return t


def main():
    markers = mop.ref_markers()
    if not markers:
        raise SystemExit("REF_MARKERS not found in app.html: refusing to build unlabelled pages")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    deals = data.get("deals") or []
    checked = data.get("last_updated") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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
            continue
        sk = mop.store_key(d)
        st = pol.state_for(mop.STATE, d.get("store"))
        referral = mop.is_referral(d, markers)
        verified = bool(st.get("conditions")) and bool(st.get("last_checked")) and bool(st.get("source_url"))
        if not (referral or verified):
            continue  # no page for offers we cannot describe properly
        groups.setdefault((sk, t), []).append(d)
    if OUT.exists():
        shutil.rmtree(OUT)  # generated content only; stale pages must not survive
    indexed, noindex = [], []
    for (sk, t), ds in groups.items():
        store_label = html.unescape(str(ds[0].get("store", "")))
        if pol.key(store_label) in SKIP_SLUGS or sk in SKIP_SLUGS:
            continue
        if "freetrade" in sk or sk.startswith("trading"):
            continue
        ds.sort(key=lambda x: (str(x.get("last_verified") or ""), str(x.get("deal_price") or "")), reverse=True)
        base = mop._slug("{} {}".format(store_label, t))
        slug, n = base, 2
        existing = {p.name for p in OUT.glob("*")} if OUT.exists() else set()
        while slug in existing:
            slug = "{}-{}".format(base, n)
            n += 1
        rows = [(d, pol.state_for(mop.STATE, d.get("store"))) for d in ds]
        build_page(store_label, t, rows, today, slug, markers)
        st = rows[0][1]
        (indexed if st.get("last_checked") else noindex).append(slug)
    (OUT / "index.json").write_text(json.dumps(
        {"checked": today, "pages": sorted(indexed), "noindex": sorted(noindex)}, indent=1), encoding="utf-8")
    print("pages: {} ({} indexed, {} noindex)".format(len(indexed) + len(noindex), len(indexed), len(noindex)))


if __name__ == "__main__":
    main()
