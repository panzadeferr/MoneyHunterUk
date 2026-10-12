"""Sitemap generator for Money Hunters UK.

Reads the deal payload the scraper builds and writes sitemap.xml with
lastmod dates that follow the data, so search engines re-crawl the day
new deals land. Usable standalone:  python3 make_sitemap.py
"""
import json
from datetime import datetime, timezone

SITE = "https://moneyhunters.co.uk/"
SITEMAP_PATH = "sitemap.xml"

# (path, changefreq, priority)
PAGES = [
    ("", "daily", "1.0"),
    ("app.html", "daily", "0.9"),
    ("bank-switch.html", "weekly", "0.8"),
    ("privacy.html", "monthly", "0.3"),
]


def write_sitemap(payload=None):
    last_updated = None
    if payload and payload.get("last_updated"):
        last_updated = str(payload["last_updated"])[:10]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lastmod = last_updated or today

    rows = []
    for path, freq, priority in PAGES:
        rows.append(
            "  <url>\n"
            f"    <loc>{SITE}{path}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(xml)
    return SITEMAP_PATH


if __name__ == "__main__":
    try:
        payload = json.load(open("all_deals.json", encoding="utf-8"))
    except Exception:
        payload = None
    print("wrote", write_sitemap(payload))
