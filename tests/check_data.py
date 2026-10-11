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
        expected = index_data.get("counts", {}).get(topic)
        if expected is not None and len(part.get("questions", [])) != expected:
            extra = [q.get("id") for q in part.get("questions", [])[expected:]]
            fail(f"{fname}: {len(part.get('questions', []))} questions but index counts {topic}={expected}; ids not in index counts: {extra[:10]}")
        qs.extend(part.get("questions", []))
    ids = [q.get("id") for q in qs]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        fail(f"duplicate question ids across topic files: {dups[:10]}")
    inv_file = index_data.get("investigations_file")
    if inv_file:
        ipath = qdir / inv_file
        if not ipath.exists():
            fail(f"data/questions/index.json: investigations_file {inv_file} is missing")
        else:
            inv = json.loads(ipath.read_text(encoding="utf-8")).get("investigations", [])
            exp_inv = index_data.get("investigations_count")
            if exp_inv is not None and len(inv) != exp_inv:
                fail(f"{inv_file}: {len(inv)} investigations but index counts {exp_inv}")
            inv_ids = [i.get("id") for i in inv]
            inv_dups = sorted({i for i in inv_ids if inv_ids.count(i) > 1})
            if inv_dups:
                fail(f"duplicate investigation ids: {inv_dups[:10]}")
            print(f"Investigation checks passed: {len(inv)} investigations, no duplicate ids.")
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

# --- playbook.json checks ---
pb_path = pathlib.Path("data/playbook.json")
if pb_path.exists():
    pb = json.loads(pb_path.read_text())
    pb_chs = pb.get("chapters", [])
    if not pb_chs:
        fail("data/playbook.json: no chapters")
    ALLOWED_BLOCKS = {"p", "h", "key", "steps", "warn", "tip", "list"}
    ALLOWED_STATUS = {"written", "new", "expand"}
    app_text = pathlib.Path("app.html").read_text() if pathlib.Path("app.html").exists() else ""
    seen_pb = {}
    for ch in pb_chs:
        if not ch.get("id") or not ch.get("title"):
            fail(f"playbook.json: chapter missing id/title: {ch.get('id')}")
        for a in ch.get("articles", []):
            aid = a.get("id")
            if not aid:
                fail(f"playbook.json: article in {ch.get('id')} missing id")
                continue
            if aid in seen_pb:
                fail(f"playbook.json: duplicate article id {aid}")
            seen_pb[aid] = True
            st = a.get("status")
            if st not in ALLOWED_STATUS:
                fail(f"playbook.json: {aid} bad status {st!r}")
            body = a.get("body")
            if body is not None and not isinstance(body, (str, list)):
                fail(f"playbook.json: {aid} body must be string or block list")
            if isinstance(body, list):
                for b in body:
                    if not isinstance(b, dict) or b.get("type") not in ALLOWED_BLOCKS:
                        fail(f"playbook.json: {aid} bad block {b if not isinstance(b, dict) else b.get('type')!r}")
                    if b.get("type") in ("key", "steps", "list") and not isinstance(b.get("items"), list):
                        fail(f"playbook.json: {aid} block {b.get('type')} missing items list")
            for src in a.get("sources", []):
                if not str(src).startswith("https://"):
                    fail(f"playbook.json: {aid} non-https source {src!r}")
            eg = a.get("existing_guide")
            if eg and app_text and eg not in app_text:
                fail(f"playbook.json: {aid} existing_guide {eg} not found in app.html")
    n_bodies = sum(1 for ch in pb_chs for a in ch.get("articles", []) if a.get("body"))
    print(f"Playbook checks passed: {len(pb_chs)} chapters, {len(seen_pb)} articles, {n_bodies} with bodies.")
else:
    print("note: data/playbook.json not present, playbook checks skipped")
if not maps:
    print("note: no game/maps/*.tmj present yet, map checks skipped")

if errors:
    print("DATA CHECKS FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"Data checks passed: {len(deals)} deals, {len(seen_bank)} bank switches.")
