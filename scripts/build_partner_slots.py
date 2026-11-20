"""Publishes partner ad slots only when their feature flag is on.

Reads config/feature_flags.json and partners/*.json (neither is deployed) and writes
data/partner-slots.json, which the homepage and app read at runtime. With every flag false the
file is {"slots": []} and nothing about the partner appears anywhere on the site.

Usage: python3 scripts/build_partner_slots.py [--out DIR] [--enable trading-com]
  --enable   build as if the flag were true (used by tests; never writes into the repo unless --out is the repo)
The draft partner page is written by scripts/build_guide_pages.py (it reuses the guide page template).
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAG_FOR = {"trading-com": "TRADING_COM_ENABLED"}


def load():
    flags = json.loads((ROOT / "config" / "feature_flags.json").read_text(encoding="utf-8"))
    partners = {}
    for p in sorted((ROOT / "partners").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        partners[d["id"]] = d
    return flags, partners


def enabled_partners(force=()):
    """Partners whose flag is true. MH_FORCE_PARTNERS=trading-com forces one on (tests only)."""
    force = tuple(force) + tuple(x for x in os.environ.get("MH_FORCE_PARTNERS", "").split(",") if x)
    flags, partners = load()
    return [partners[i] for i in partners if flags.get(FLAG_FOR.get(i, ""), False) or i in force]


def slots_json(force=()):
    slots = []
    for p in enabled_partners(force):
        c = p["card"]
        guide_ok = True
        slots.append({
            "id": p["id"],
            "placements": p["placements"],
            "ad_label": c["ad_label"],
            "provider": p["provider"],
            "headline": c["headline"],
            "body": c["body"],
            "risk": c["risk"],
            "cta": c["cta"],
            "url": p.get("referral_url", ""),
            "utm": p.get("utm", {}),
            "events": p["events"],
            "guide_url": "/guides/{}/".format(p["guide_slug"]) if guide_ok else "",
            "guide_cta": c["guide_cta"],
        })
    return {"slots": slots}


def main():
    out = ROOT
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    force = ()
    if "--enable" in sys.argv:
        force = (sys.argv[sys.argv.index("--enable") + 1],)
    target = out / "data" / "partner-slots.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(slots_json(force), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("partner slots: {} published".format(len(slots_json(force)["slots"])))


if __name__ == "__main__":
    main()
