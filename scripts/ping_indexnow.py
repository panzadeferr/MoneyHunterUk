#!/usr/bin/env python3
"""Ping IndexNow (Bing and friends) with all live sitemap URLs so new deals get
indexed fast. The key file 9ba589cb48714f42873c1a25a4e74641.txt must be deployed at the site root first."""
import json, re, sys, urllib.request

SITE = "https://moneyhunters.co.uk"
KEY = "9ba589cb48714f42873c1a25a4e74641"

def sitemap_urls():
    xml = urllib.request.urlopen(f"{SITE}/sitemap.xml", timeout=30).read().decode()
    return sorted(set(re.findall(r"<loc>([^<]+)</loc>", xml)))

def main():
    urls = sitemap_urls()
    if not urls:
        print("no urls in sitemap"); return 1
    body = json.dumps({
        "host": "moneyhunters.co.uk",
        "key": KEY,
        "keyLocation": f"{SITE}/{KEY}.txt",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=body, headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        print("indexnow status:", r.status)
    return 0

if __name__ == "__main__":
    sys.exit(main())
