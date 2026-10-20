"""Write sitemap.xml for every public page. Run during deploy.

lastmod follows all_deals.json's last_updated when available, so search
engines re-crawl the day new deals land; falls back to today's date."""
import datetime, json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
today = datetime.date.today().isoformat()
try:
    payload = json.loads((root / "all_deals.json").read_text(encoding="utf-8"))
    today = str(payload.get("last_updated", today))[:10]
except Exception:
    pass
pages = [("", "1.0", "weekly"), ("app.html", "0.9", "daily"), ("bank-switch.html", "0.8", "weekly"), ("privacy.html", "0.3", "monthly")]
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, prio, freq in pages:
    out += ["  <url>", f"    <loc>https://moneyhunters.co.uk/{path}</loc>", f"    <lastmod>{today}</lastmod>", f"    <changefreq>{freq}</changefreq>", f"    <priority>{prio}</priority>", "  </url>"]
# guide pages (built by scripts/build_guide_pages.py)
import re
gdir = root / "guides"
if gdir.is_dir():
    out += ["  <url>", "    <loc>https://moneyhunters.co.uk/guides/</loc>", f"    <lastmod>{today}</lastmod>", "    <changefreq>weekly</changefreq>", "    <priority>0.8</priority>", "  </url>"]
    for f in sorted(gdir.glob("*/index.html")):
        m = re.search(r'"dateModified": "(\d{4}-\d{2}-\d{2})"', f.read_text(encoding="utf-8"))
        out += ["  <url>", f"    <loc>https://moneyhunters.co.uk/guides/{f.parent.name}/</loc>", f"    <lastmod>{m.group(1) if m else today}</lastmod>", "    <changefreq>monthly</changefreq>", "    <priority>0.7</priority>", "  </url>"]
out.append("</urlset>")
(root / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")
print("sitemap.xml written for", today)
