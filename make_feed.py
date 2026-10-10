"""Atom feed generator for Money Hunters UK.

Reads the deal payload the scraper builds and writes feed.xml so
deal readers and aggregators can pick up the latest verified offers.
Usable standalone:  python3 make_feed.py
"""
import json
from datetime import datetime, timezone
from xml.sax.saxutils import escape

SITE = "https://moneyhunters.co.uk/"
FEED_PATH = "feed.xml"
MAX_ENTRIES = 30
_PLACEHOLDER_EXPIRY = "2026-12-31"


def _rfc3339(value):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%dT%H:%M:%SZ")
        except (TypeError, ValueError):
            continue
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _summary(deal):
    bits = []
    for key, label in (
        ("deal_price", "Price"),
        ("original_price", "Was"),
        ("saving_percent", "Saving"),
        ("best_payment_method", "Best payment"),
    ):
        value = deal.get(key)
        if value not in (None, "", 0, "0", 999, "999"):
            bits.append(f"{label}: {value}")
    expiry = deal.get("expires") or deal.get("expires_at") or deal.get("expiry")
    if expiry and str(expiry) != _PLACEHOLDER_EXPIRY:
        bits.append(f"Ends: {expiry}")
    store = deal.get("store") or "Deal"
    return escape("; ".join(bits) or f"{store} offer listed on Money Hunters UK")


def write_feed(output, path=FEED_PATH):
    """Write feed.xml from the scraper's output dict (or a parsed all_deals.json)."""
    deals = output.get("deals", [])
    seen_links = set()
    entries = []
    for deal in deals:
        link = (deal.get("link") or "").strip()
        if not link or link in seen_links:
            continue
        seen_links.add(link)
        title = escape(f"{deal.get('store') or 'Deal'}: {deal.get('item') or 'offer'}")
        link_attr = escape(link, {'"': '&quot;'})
        entries.append(
            "  <entry>\n"
            f"    <title>{title}</title>\n"
            f'    <link rel="alternate" href="{link_attr}"/>\n'
            f"    <id>{link_attr}</id>\n"
            f"    <updated>{_rfc3339(output.get('last_updated'))}</updated>\n"
            f"    <summary>{_summary(deal)}</summary>\n"
            "  </entry>"
        )
        if len(entries) >= MAX_ENTRIES:
            break
    feed_updated = _rfc3339(output.get("last_updated"))
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        "  <title>Money Hunters UK: latest deals</title>\n"
        f"  <id>{SITE}</id>\n"
        f'  <link rel="self" href="{SITE}feed.xml"/>\n'
        f'  <link rel="alternate" href="{SITE}"/>\n'
        f"  <updated>{feed_updated}</updated>\n"
        "  <subtitle>UK bank switch, cashback and referral offers, updated daily</subtitle>\n"
        + "\n".join(entries)
        + "\n</feed>\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    return path


if __name__ == "__main__":
    with open("all_deals.json", encoding="utf-8") as f:
        write_feed(json.load(f))
    print(f"wrote {FEED_PATH}")
