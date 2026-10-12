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
out.append("</urlset>")
(root / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")
print("sitemap.xml written for", today)
