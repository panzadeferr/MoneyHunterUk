#!/usr/bin/env python3
"""Checks for the generated per-offer pages (offers/<slug>/index.html).

Covers Albertino's PR #111 review points: page set matches offers/index.json,
sitemap lists exactly the indexed pages, no code leakage, no Freetrade or
trading.com pages, Ad label on every referral link, risk warning on investing
pages, no forbidden wording in visible text, noindex on unverified pages,
Umami analytics on every page.
Run: python3 tests/check_offer_pages.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFERS = ROOT / "offers"
CODES = ["J2SK9W", "z8w4m6", "8TGF"]
FORBIDDEN = [r"\bfree\b", r"\bguaranteed\b", r"\brisk[- ]free\b", r"\beasy\s+money\b"]
RISK_SNIPPET = "Capital at risk"

errors = []
reg_path = OFFERS / "index.json"
if not reg_path.exists():
    print("FAIL: offers/index.json missing"); sys.exit(1)
reg = json.loads(reg_path.read_text(encoding="utf-8"))
pages, noindex = reg.get("pages", []), reg.get("noindex", [])


def visible(path):
    t = path.read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return t


dirs = sorted(p.name for p in OFFERS.iterdir() if p.is_dir())
if dirs != sorted(pages + noindex):
    errors.append("page set on disk does not match index.json (stale or missing pages)")

sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
sm_urls = set(re.findall(r"<loc>https://moneyhunters\.co\.uk(/offers/[^<]*)</loc>", sm))
expected = {"/offers/{}/".format(s) for s in pages}
if sm_urls != expected:
    errors.append("sitemap /offers/ URLs do not equal the indexed pages: sitemap-only={}, page-only={}".format(
        sorted(sm_urls - expected), sorted(expected - sm_urls)))

for slug in dirs:
    f = OFFERS / slug / "index.html"
    if not f.exists():
        errors.append(slug + ": index.html missing"); continue
    t = f.read_text(encoding="utf-8")
    vis = visible(f)
    if 'data-website-id="f9d2c068' not in t or "mhTrack" not in t or "offer-click" not in t:
        errors.append(slug + ": Umami snippet or offer-click tracking missing")
    for rx in FORBIDDEN:
        if re.search(rx, vis, re.I):
            errors.append(slug + ": forbidden wording matches " + rx)
    joined = t + vis
    for code in CODES:
        if code in t or code.lower() in vis.lower():
            errors.append(slug + ": referral code visible: " + code)
    for a in re.finditer(r'<a [^>]*rel="sponsored[^"]*"[^>]*>', t):
        ctx = t[max(0, a.start() - 120): a.end()]
        if 'class="tag">Ad</span>' not in ctx:
            errors.append(slug + ": referral link without adjacent Ad label")
    low = vis.lower()
    if "freetrade" in low or "trading.com" in low:
        errors.append(slug + ": names Freetrade or trading.com in visible text")
    if slug in noindex:
        if 'content="noindex"' not in t:
            errors.append(slug + ": listed noindex but meta robots missing")
    else:
        if 'content="noindex"' in t:
            errors.append(slug + ": indexed page carries noindex")
    if slug.endswith("-invest") and RISK_SNIPPET not in vis:
        errors.append(slug + ": investing page without risk warning")

if "freetrade" in " ".join(dirs) or any(d.startswith("trading") for d in dirs):
    errors.append("a Freetrade or trading.com page directory exists")

total = len(dirs)
print("offer pages: {} ({} indexed, {} noindex)".format(total, len(pages), len(noindex)))
if total < 5:
    errors.append("page set suspiciously small: {}".format(total))
if errors:
    print("Offer pages check FAILED:")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
print("Offer pages check passed")
