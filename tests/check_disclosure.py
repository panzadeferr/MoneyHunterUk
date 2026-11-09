#!/usr/bin/env python3
"""Affiliate disclosure check (CAP Code / ASA), added 9 Nov 2026.

Hard-fails if any referral link or referral code on the public pages is shown
without an "Ad" label. Referral markers are read from REF_MARKERS in app.html,
the single source of truth also used by the app and scripts/make_offers_page.py.

- offers.html: every offer block whose link or text contains a marker must
  carry <span class="ad">Ad</span>, and the old "plain retailer pages" wording
  must not come back.
- index.html, bank-switch.html, guides/*: any link containing a marker must
  sit in a block that mentions "Ad" plus "referral" or "commission".
"""
import glob
import re
import sys

app = open("app.html", encoding="utf-8").read()
m = re.search(r"const REF_MARKERS=\[(.*?)\];", app, re.S)
if not m:
    print("FAIL: REF_MARKERS not found in app.html")
    sys.exit(1)
MARKERS = re.findall(r"'([^']+)'", m.group(1))
errors = []

offers = open("offers.html", encoding="utf-8").read()
if "plain retailer pages" in offers:
    errors.append("offers.html: says links are plain retailer pages")
for block in re.findall(r'<div class="offer"[^>]*>(.*?)</div>', offers, re.S):
    if any(mk in block for mk in MARKERS) and 'class="ad"' not in block:
        title = re.sub(r"<[^>]+>", " ", block)[:70]
        errors.append("offers.html: referral offer without Ad label: " + " ".join(title.split()))

pages = ["index.html", "bank-switch.html"] + glob.glob("guides/**/*.html", recursive=True)
for page in pages:
    text = open(page, encoding="utf-8").read()
    for a in re.finditer(r'<a [^>]*href="([^"]+)"', text):
        if any(mk in a.group(1) for mk in MARKERS):
            ctx = text[max(0, a.start() - 600): a.end() + 600]
            if not (re.search(r"\bAd\b", ctx) and re.search(r"referral|commission", ctx, re.I)):
                errors.append("{}: referral link without nearby Ad disclosure: {}".format(page, a.group(1)[:80]))

if errors:
    print("Disclosure check FAILED:")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
print("Disclosure check passed ({} markers, offers.html and {} pages)".format(len(MARKERS), len(pages)))
