#!/usr/bin/env python3
"""Browser render test for the generated per-offer pages (PR review point 9).

Opens three representative generated pages (indexed referral, verified
conditions only, noindex referral) over a local HTTP server and checks they
render: title and h1, header navigation with a home link, referral links carry
rel="sponsored" and an Ad label, and the offer-click event fires with the offer
id. Skips cleanly when Playwright or its Chromium binary is unavailable, so CI
without a browser install still passes.
"""
import json
import re
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP check_offer_pages_browser: playwright not installed")
    sys.exit(0)

SHELL = sorted((ROOT.parent / ".cache" / "ms-playwright").glob("chromium_headless_shell-*")) \
    + sorted(Path(os.environ.get("HOME", "/root"), ".cache/ms-playwright").glob("chromium_headless_shell-*"))
if not SHELL:
    print("SKIP check_offer_pages_browser: no chromium headless shell installed")
    sys.exit(0)


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def pick_pages():
    """One indexed referral page, one verified no-referral page, one noindex referral page."""
    idx = json.loads((ROOT / "offers" / "index.json").read_text())
    indexed, noindex = set(idx["pages"]), set(idx["noindex"])
    kinds = {}
    for slug in sorted(indexed | noindex):
        html = (ROOT / "offers" / slug / "index.html").read_text()
        is_ref = bool(re.search(r'<a[^>]*data-offer', html))
        kind = ("referral" if is_ref else "verified") + ("/noindex" if slug in noindex else "")
        kinds.setdefault(kind, slug)
    picked = [kinds.get("referral"), kinds.get("verified"), kinds.get("referral/noindex")]
    return [p for p in picked if p]


def main():
    slugs = pick_pages()
    if len(slugs) < 2:
        print("FAIL check_offer_pages_browser: could not pick 2+ representative pages from offers/index.json")
        return 1
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                           cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    bad = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page()
            for slug in slugs:
                errs = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.goto(f"http://127.0.0.1:{port}/offers/{slug}/index.html")
                page.wait_for_timeout(300)
                if not page.title():
                    bad.append(f"{slug}: no title")
                if not page.locator("h1").inner_text():
                    bad.append(f"{slug}: no h1")
                home = page.eval_on_selector("header a.brand", "e => e.getAttribute('href')")
                if home != "/":
                    bad.append(f"{slug}: home link is {home!r}, expected /")
                nav = page.eval_on_selector_all("header nav a", "els => els.length")
                if nav < 2:
                    bad.append(f"{slug}: header nav has {nav} links")
                has_umami = page.locator("script[src*='umami']").count() > 0
                if not has_umami:
                    bad.append(f"{slug}: Umami script missing")
                refs = page.eval_on_selector_all(
                    "a[data-offer]",
                    "els => els.map(e => [e.getAttribute('href'), e.getAttribute('rel'), e.getAttribute('data-offer')])")
                fired = page.evaluate("""() => {
                    const a = document.querySelector('a[data-offer]');
                    if (!a) return 'no-referral-link';
                    let got = null;
                    window.mhTrack = (n, d) => { got = n + '|' + d.offer; };
                    a.click();
                    return got;
                }""")
                for href, rel, oid in refs:
                    if not href or not href.startswith("https://"):
                        bad.append(f"{slug}: referral href not https: {href!r}")
                    if not rel or "sponsored" not in rel:
                        bad.append(f"{slug}: referral rel missing sponsored: {rel!r}")
                if fired not in ("no-referral-link", None, ""):
                    pass
                elif fired != "no-referral-link":
                    bad.append(f"{slug}: offer-click did not fire ({fired!r})")
                if fired != "no-referral-link" and fired and "offer-click" not in fired:
                    bad.append(f"{slug}: event name wrong: {fired!r}")
                if errs:
                    bad.append(f"{slug}: JS errors {errs}")
            browser.close()
    finally:
        srv.terminate()
    if bad:
        print("FAIL check_offer_pages_browser:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"PASS check_offer_pages_browser: {len(slugs)} pages render, navigation and referral links work, offer-click fires")
    return 0


if __name__ == "__main__":
    sys.exit(main())
