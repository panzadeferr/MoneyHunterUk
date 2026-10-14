#!/usr/bin/env python3
"""Sovrn link swap for moneyhunters.co.uk deals.

Reads all_deals.json and, for deals whose store is mapped in
data/sovrn_merchants.json, rewrites the plain retailer link into a
Sovrn/ShareASale tracked link.

Default mode is DRY-RUN: it prints what would change and writes nothing.
Only --apply writes, and only when the merchant map is non-empty.
No site copy, no deal content and no prices are touched: links only.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, urlencode

ROOT = Path(__file__).resolve().parent.parent
DEALS = ROOT / "all_deals.json"
MAP = ROOT / "data" / "sovrn_merchants.json"

# Sovrn Commerce (ShareASale) direct-link pattern, merchantID filled per merchant.
# afftrack carries the deal id so provider-confirmed clicks stay attributable.
TEMPLATE = "https://www.shareasale.com/m-pr.cfm?merchantID={merchant_id}&u={url}&afftrack={afftrack}"


def load(path, what):
    if not path.exists():
        sys.exit(f"missing {what}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def host_of(url):
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except ValueError:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write all_deals.json (refused while the merchant map is empty)")
    args = ap.parse_args()

    data = load(DEALS, "deal data")
    deals = data.get("deals", [])
    mapping = load(MAP, "merchant map").get("merchants", {})

    if args.apply and not mapping:
        sys.exit("refusing to apply: data/sovrn_merchants.json has no merchants yet")

    changes, unmapped_stores = [], set()
    for deal in deals:
        store, link = deal.get("store", ""), deal.get("link", "")
        merchant_id = mapping.get(store)
        if not merchant_id:
            if link and "shareasale.com" not in link:
                unmapped_stores.add(store)
            continue
        host = host_of(link)
        if not host or "shareasale.com" in link:
            continue  # already tracked or not a merchant link (e.g. Reddit source)
        tracked = TEMPLATE.format(
            merchant_id=merchant_id,
            url=urlencode({"": link})[2:],  # url-encode the destination
            afftrack=f"mh-{deal.get('id', store)}",
        )
        changes.append((store, deal.get("item", ""), link, tracked))
        if args.apply:
            deal["link"] = tracked
            deal["last_affiliate_update"] = data.get("last_updated", "")

    verb = "APPLIED" if args.apply else "dry-run"
    print(f"{verb}: {len(changes)} link(s) would be tracked")
    for store, item, old, new in changes[:10]:
        print(f"  [{store}] {item[:40]}\n    {old}\n -> {new}")
    if len(changes) > 10:
        print(f"  ... and {len(changes) - 10} more")
    if unmapped_stores:
        print(f"stores with no merchant mapping yet ({len(unmapped_stores)}): {sorted(unmapped_stores)}")

    if args.apply:
        data["last_link_swap"] = data.get("last_updated", "")
        DEALS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {DEALS}")


if __name__ == "__main__":
    main()
