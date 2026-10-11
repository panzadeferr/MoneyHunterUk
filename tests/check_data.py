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
qpath = ROOT / "data" / "questions.json"
ppath = ROOT / "data" / "playbook.json"
pb_ids = set()
if ppath.exists():
    pdata = json.loads(ppath.read_text(encoding="utf-8"))
    for ch in pdata.get("chapters", []):
        for art in ch.get("articles", []):
            aid = str(art.get("id", "?"))
            if aid in pb_ids:
                fail(f"playbook.json: duplicate article id {aid}")
            pb_ids.add(aid)
else:
    print("note: data/playbook.json not present yet, learn_more resolution skipped")

if not qpath.exists():
    print("note: data/questions.json not present yet, question checks skipped")
else:
    qdata = json.loads(qpath.read_text(encoding="utf-8"))
    qs = qdata.get("questions", [])
    qids = set()
    for q in qs:
        qid = str(q.get("id", "?"))
        if qid in qids:
            fail(f"questions.json: duplicate id {qid}")
        qids.add(qid)
        opts = q.get("options") or []
        a = q.get("answer")
        if not opts or not isinstance(a, int) or a < 0 or a >= len(opts):
            fail(f"question {qid}: answer index out of range")
        if not q.get("explanation"):
            fail(f"question {qid}: missing explanation")
        if not q.get("question"):
            fail(f"question {qid}: missing question text")
        lm = q.get("learn_more")
        if lm and pb_ids and lm not in pb_ids:
            fail(f"question {q.get('id')}: learn_more {lm!r} is not a playbook.json article id")
        if q.get("volatile") and q.get("review_by") and str(q["review_by"])[:10] < today:
            print(f"WARNING: question {q.get('id')} is volatile and its review_by ({q['review_by']}) has passed; re-verify")
    print(f"Question checks passed: {len(qs)} questions.")


# --- game map checks (v4 port: letter-grid tmj with a legend tileset, no external images) ---
import pathlib
maps = sorted(pathlib.Path("game/maps").glob("*.tmj")) if pathlib.Path("game/maps").exists() else []
expect = {"town.tmj": (40, 36), "bank.tmj": (12, 10)}
for mp in maps:
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{mp}: invalid JSON ({e})")
        continue
    w, h = m.get("width", 0), m.get("height", 0)
    exp = expect.get(mp.name)
    if exp and (w, h) != exp:
        fail(f"{mp}: expected {exp[0]}x{exp[1]}, got {w}x{h}")
    layers = {l.get("name"): l for l in m.get("layers", [])}
    if "ground" not in layers:
        fail(f"{mp}: missing 'ground' layer")
        continue
    if len(layers["ground"].get("data", [])) != w * h:
        fail(f"{mp}: 'ground' layer length != width*height")
    legend = ""
    for ts in m.get("tilesets", []):
        for p in ts.get("properties", []):
            if p.get("name") == "legend":
                legend = p.get("value", "")
    if not legend:
        fail(f"{mp}: missing legend property on tileset")
    else:
        mx = max(layers["ground"].get("data", [1])) if layers["ground"].get("data") else 0
        if mx > len(legend):
            fail(f"{mp}: gid {mx} exceeds legend length {len(legend)}")
    for ts in m.get("tilesets", []):
        img = ts.get("image")
        if img:
            fail(f"{mp}: tileset image {img!r} not allowed (v4 maps draw procedurally, legend-only tileset)")
    print(f"Map checks passed: {mp.name} ({w}x{h}, legend {len(legend)} chars).")
if not maps:
    print("note: no game/maps/*.tmj present yet, map checks skipped")

if errors:
    print("DATA CHECKS FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"Data checks passed: {len(deals)} deals, {len(seen_bank)} bank switches.")
