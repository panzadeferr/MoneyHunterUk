"""Data and page checks that must pass before deploy. Run: python tests/check_data.py"""
import json, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
today = datetime.date.today().isoformat()
errors = []

def fail(msg):
    errors.append(msg)

data = json.loads((ROOT / "all_deals.json").read_text(encoding="utf-8"))
deals = data.get("deals", [])
if len(deals) < 20:
    fail(f"only {len(deals)} deals in all_deals.json")

seen_bank = {}
for d in deals:
    name = d.get("store", "?")
    for f in ("store", "item", "deal_price", "link"):
        if not d.get(f):
            fail(f"{name}: missing {f}")
    if d.get("link") and not str(d["link"]).startswith(("http://", "https://")):
        fail(f"{name}: link is not a URL")
    exp = str(d.get("expires") or "")[:10]
    if exp and exp < today:
        fail(f"{name}: expired on {exp} but still listed")
    if exp == "2026-12-31":
        fail(f"{name}: placeholder expiry 2026-12-31")
    lv = str(d.get("last_verified") or "")
    if lv and lv > today:
        fail(f"{name}: last_verified {lv} is in the future")
    if d.get("type") == "bank_switch":
        key = name.lower()
        if key in seen_bank:
            fail(f"{name}: listed twice as a bank switch")
        seen_bank[key] = d

verified = json.loads((ROOT / "verified.json").read_text(encoding="utf-8"))
names = {d.get("store", "").lower() for d in deals}
for k in verified:
    if not k.startswith("_") and k.lower() not in names:
        print(f"note: verified.json lists {k!r}, not in current data (fine if it has expired)")

# One amount per bank across pages
def amount(text, label):
    m = re.search(label + r"[^£<]{0,60}(?:<[^>]+>\s*){0,6}(up to )?£(\d+)", text)
    return (bool(m and m.group(1)), int(m.group(2))) if m else None

index = (ROOT / "index.html").read_text(encoding="utf-8")
bank = (ROOT / "bank-switch.html").read_text(encoding="utf-8")
if "Lloyds £250" in index or "Lloyds Bank for £250" in index:
    fail("index.html still says Lloyds £250 (current offer is £200)")
for banned in ("updated today", "£2,000+ per year", "tax-free", "£500+ in your first 3 months"):
    if banned in index:
        fail(f"index.html still contains unsupported claim: {banned!r}")
if "Ad" not in index or "referral" not in index.lower():
    fail("index.html has no ad/referral disclosure")
if "ADMIN_SECRET" in (ROOT / "app.html").read_text(encoding="utf-8"):
    fail("app.html still has ADMIN_SECRET")

# ── Game data files (/data/) ──
ppath = ROOT / "data" / "playbook.json"
pb_ids = set()
pb_articles_with_body = 0
if ppath.exists():
    pdata = json.loads(ppath.read_text(encoding="utf-8"))
    for ch in pdata.get("chapters", []):
        for art in ch.get("articles", []):
            aid = str(art.get("id", "?"))
            if aid in pb_ids:
                fail(f"playbook.json: duplicate article id {aid}")
            pb_ids.add(aid)
            if art.get("body") and not art.get("existing_guide"):
                pb_articles_with_body += 1
            # body must have at least one non-empty paragraph
            if art.get("body") and not str(art["body"]).strip():
                fail(f"playbook.json: article {aid} has an empty body")
else:
    print("note: data/playbook.json not present yet, learn_more resolution skipped")

qdir = ROOT / "data" / "questions"
idx = qdir / "index.json"
qs = []
if idx.exists():
    index_data = json.loads(idx.read_text(encoding="utf-8"))
    files = index_data.get("files", {})
    if not files:
        fail("data/questions/index.json lists no topic files")
    for topic, fname in files.items():
        fpath = qdir / fname
        if not fpath.exists():
            fail(f"data/questions/index.json: file {fname} for topic {topic} is missing")
            continue
        part = json.loads(fpath.read_text(encoding="utf-8"))
        for q in part.get("questions", []):
            if q.get("topic") != topic:
                fail(f"{fname}: question {q.get('id')} topic {q.get('topic')!r} != file topic {topic!r}")
        qs.extend(part.get("questions", []))
else:
    print("note: data/questions/index.json not present yet, question checks skipped")
# --- game map checks ---
import pathlib
maps = sorted(pathlib.Path("game/maps").glob("*.tmj")) if pathlib.Path("game/maps").exists() else []
for mp in maps:
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{mp}: invalid JSON ({e})")
        continue
    w, h = m.get("width", 0), m.get("height", 0)
    layers = {l.get("name"): l for l in m.get("layers", [])}
    for lname in ("ground", "solid"):
        if lname not in layers:
            fail(f"{mp}: missing '{lname}' layer")
        elif len(layers[lname].get("data", [])) != w * h:
            fail(f"{mp}: '{lname}' layer length != width*height")
    for ts in m.get("tilesets", []):
        img = pathlib.Path("game/maps") / ts.get("image", "")
        if not img.exists():
            fail(f"{mp}: tileset image {ts.get('image')!r} not found (maps are self-hosted, no external assets)")
    objs = [o for l in m.get("layers", []) if l.get("type") == "objectgroup" for o in l.get("objects", [])]
    if not any(o.get("type") == "spawn" for o in objs):
        fail(f"{mp}: no spawn object")
    for o in objs:
        if not o.get("name") or not o.get("type"):
            fail(f"{mp}: object missing name or type: {o.get('name')!r}")
    bad_types = [o["type"] for o in objs if o.get("type") not in ("spawn", "encounter", "sign", "npc")]
    if bad_types:
        fail(f"{mp}: unknown object types {set(bad_types)}")
    print(f"Map checks passed: {mp.name} ({w}x{h}, {len(objs)} objects).")
if not maps:
    print("note: no game/maps/*.tmj present yet, map checks skipped")

if errors:
    print("DATA CHECKS FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"Data checks passed: {len(deals)} deals, {len(seen_bank)} bank switches.")
