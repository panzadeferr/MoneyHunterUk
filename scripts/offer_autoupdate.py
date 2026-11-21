"""Offer auto-update policy (switched OFF: config/autoupdate.json has auto_apply=false).

The scraper is the only writer. Wajo, Fo, Instinct and Claude only report: apply() refuses any other writer.

Allowed automatically (when auto_apply is true and the kill switch is off):
  - mark an offer ended (its provider page is gone, or its expiry has passed)
  - update an amount read from the provider's OWN page when the change is within max_change_pct (30%)
  - set last_checked (checked_by=fetch) after a real fetch of the provider's page that matched
Never automatic: adding offers, changing referral/affiliate links, wording, Ad labels or risk warnings,
investing offers, Trading.com, or any change over the limit (those are queued for Alberto).
Controls: before/after change log with source URL and timestamp, daily Telegram digest, one-step revert,
CI checks must pass (else rolled back), kill switch (config or MH_AUTOUPDATE_KILL=1).
Everything read from a third-party page is data only: it is never executed, never used as an instruction,
and only amounts are parsed out of it.
"""
import json, os, re, sys, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer_policy as pol  # noqa: E402

ROOT = pol.ROOT
CFG_PATH = ROOT / "config" / "autoupdate.json"
ALLOWED_FIELDS = {"status", "amount_override", "last_checked"}  # last_checked also sets checked_by=fetch
FORBIDDEN_NAME_RX = re.compile(r"link|url|referral|affiliate|item|wording|ad_label|risk|text|name|add", re.I)


def load_cfg():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))


def kill_switch_on(cfg):
    return bool(cfg.get("kill_switch")) or os.environ.get("MH_AUTOUPDATE_KILL") == "1"


def money(text):
    m = re.search(r"£\s?([\d,]+(?:\.\d+)?)", str(text or ""))
    return float(m.group(1).replace(",", "")) if m else None


def extract_amount(page_text, keywords=("bonus", "switch", "reward", "get", "earn", "offer")):
    """Amounts near an offer keyword. Page text is data only. Returns sorted distinct £ values."""
    found = set()
    t = re.sub(r"\s+", " ", str(page_text or ""))[:400000]
    for m in re.finditer(r"£\s?([\d,]+(?:\.\d+)?)", t):
        ctx = t[max(0, m.start() - 80): m.end() + 80].lower()
        if any(k in ctx for k in keywords):
            found.add(float(m.group(1).replace(",", "")))
    return sorted(found)


def hosts_match(a, b):
    ha, hb = urllib.parse.urlparse(a).hostname or "", urllib.parse.urlparse(b).hostname or ""
    strip = lambda h: h[4:] if h.startswith("www.") else h
    return bool(ha) and strip(ha) == strip(hb)


def fetch_observation(key, rec, current_amount, timeout=15):
    """Real fetch of the provider's own page. Never raises; failures are status=error and stamp nothing."""
    url = rec.get("source_url", "")
    obs = {"key": key, "url": url, "status": "error", "matched": False, "amounts": []}
    try:
        if not url.startswith("https://"):
            return obs
        req = urllib.request.Request(url, headers={"User-Agent": "MoneyHuntersBot/1.0 (+https://moneyhunters.co.uk)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            final = r.geturl()
            if not hosts_match(url, final):
                return obs  # redirected off the provider's site
            body = r.read(600000).decode("utf-8", "ignore")
        text = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", body, flags=re.S | re.I)
        obs["status"] = "ok"
        obs["amounts"] = extract_amount(text)
        cur = money(current_amount)
        obs["matched"] = cur is not None and cur in obs["amounts"]
    except urllib.error.HTTPError as e:
        obs["status"] = "gone" if e.code in (404, 410) else "error"
    except Exception:
        obs["status"] = "error"
    return obs


def refusal(key, rec):
    """Why this provider may never be changed automatically, or None."""
    if not rec:
        return "not an existing offer (adding offers is never automatic)"
    if pol.is_investing(rec):
        return "investing offer"
    if re.search(r"trading[-.]?com|tradingcom", key + rec.get("provider", ""), re.I):
        return "Trading.com"
    if rec.get("hidden"):
        return "hidden offer"
    if not (rec.get("source_is_provider_page") and rec.get("source_url")):
        return "no provider page recorded as source"
    return None


def plan(observations, state, current_amounts, cfg, today):
    """Turn observations into proposed changes. decision: auto | queue | reject."""
    out = []
    limit = float(cfg.get("max_change_pct", 30))
    for o in observations:
        key = o["key"]; rec = state.get(key)
        why = refusal(key, rec)
        base = {"key": key, "source_url": o.get("url", ""), "observed_at": today}
        if why:
            out.append(dict(base, kind="none", decision="reject", reason=why)); continue
        if not hosts_match(o.get("url", ""), rec["source_url"]):
            out.append(dict(base, kind="none", decision="reject", reason="observation is not from the recorded provider page")); continue
        if o["status"] == "gone":
            out.append(dict(base, kind="mark_ended", field="status", before=rec.get("status"), after="ended", decision="auto", reason="provider page is gone")); continue
        if o["status"] != "ok":
            out.append(dict(base, kind="none", decision="reject", reason="fetch failed: nothing is stamped")); continue
        if not o.get("matched"):
            cur = money(current_amounts.get(key))
            seen = o.get("amounts") or []
            if cur and len(seen) == 1:
                pct = abs(seen[0] - cur) / cur * 100
                out.append(dict(base, kind="amount", field="amount_override", before=current_amounts.get(key), after="£{:g}".format(seen[0]),
                                pct=round(pct, 1), decision="auto" if pct <= limit else "queue",
                                reason="amount read from provider page, change {:.1f}%".format(pct) + ("" if pct <= limit else " is over the {:g}% limit".format(limit))))
            else:
                out.append(dict(base, kind="none", decision="reject", reason="page did not match and its amount is missing or ambiguous: needs a person"))
            continue
        out.append(dict(base, kind="last_checked", field="last_checked", before=rec.get("last_checked"), after=today, decision="auto", reason="real fetch matched the provider page"))
    return out


def valid_change(c):
    return c.get("field") in ALLOWED_FIELDS and not FORBIDDEN_NAME_RX.search(str(c.get("field")))


def run_ci_checks():
    r = subprocess.run([sys.executable, "-c", "import glob,subprocess,sys;fs=sorted(glob.glob('tests/check_*.py'));sys.exit(max([subprocess.run([sys.executable,f]).returncode for f in fs] or [0]))"], cwd=ROOT, capture_output=True)
    return r.returncode == 0


def apply(changes, state, cfg, writer, today, log, ci_check=run_ci_checks, now=None):
    """Apply auto changes to `state` (in place) and append to `log`. Returns (applied, queued, notes)."""
    notes = []
    applied = []
    queued = [c for c in changes if c["decision"] == "queue"]
    if writer != cfg.get("writer", "scraper"):
        return [], queued, ["refused: only the scraper may write (writer=%s)" % writer]
    if kill_switch_on(cfg):
        return [], queued, ["kill switch is on: nothing applied"]
    if not cfg.get("auto_apply"):
        return [], queued, ["auto_apply is false: dry run, nothing applied"]
    snapshot = json.dumps(state)
    run_id = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    for c in changes:
        if c["decision"] != "auto" or not valid_change(c):
            continue
        rec = state[c["key"]]
        entry = dict(c, run_id=run_id, timestamp=(now or datetime.now(timezone.utc)).isoformat(timespec="seconds"))
        if c["field"] == "last_checked":
            entry["before"] = {"last_checked": rec.get("last_checked"), "checked_by": rec.get("checked_by")}
            rec["last_checked"] = c["after"]; rec["checked_by"] = "fetch"
            entry["after"] = {"last_checked": c["after"], "checked_by": "fetch"}
        elif c["field"] == "status":
            rec["status"] = c["after"]
        elif c["field"] == "amount_override":
            entry["before"] = rec.get("amount_override")
            rec["amount_override"] = {"value": c["after"], "source_url": c["source_url"], "date": today}
            entry["after"] = rec["amount_override"]
        applied.append(entry)
    if applied and not ci_check():
        state.clear(); state.update(json.loads(snapshot))
        notes.append("CI checks failed: changes rolled back")
        return [], queued, notes
    log.extend(applied)
    return applied, queued, notes


def revert(run_id, state, log):
    """One-step revert of a run: restores the logged before values (only where the current value is still the logged after)."""
    n = 0
    for e in [x for x in log if x.get("run_id") == run_id and not x.get("reverted")]:
        rec = state.get(e["key"])
        if not rec:
            continue
        if e["field"] == "last_checked":
            rec["last_checked"] = e["before"]["last_checked"]; rec["checked_by"] = e["before"]["checked_by"]
        elif e["field"] == "status":
            rec["status"] = e["before"]
        elif e["field"] == "amount_override":
            if e["before"] is None: rec.pop("amount_override", None)
            else: rec["amount_override"] = e["before"]
        e["reverted"] = True; n += 1
    return n


def digest_text(today, changes, applied, queued, notes):
    lines = ["Money Hunters offer check {}".format(today)]
    lines.append("Applied: {} · Queued for you: {} · Rejected: {}".format(len(applied), len(queued), sum(1 for c in changes if c["decision"] == "reject")))
    lines += ["- " + n for n in notes]
    for c in queued:
        lines.append("QUEUED {}: {} -> {} ({})".format(c["key"], c.get("before"), c.get("after"), c["reason"]))
    for c in applied[:10]:
        lines.append("APPLIED {}: {} ({})".format(c["key"], c["kind"], c["source_url"]))
    if not applied and not queued:
        lines.append("No changes.")
    return "\n".join(lines)[:3500]


def send_digest(text, env=None, sender=None):
    env = os.environ if env is None else env
    tok, chat = env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        return False
    if sender is None:
        def sender(t, c, m):
            data = urllib.parse.urlencode({"chat_id": c, "text": m}).encode()
            urllib.request.urlopen(urllib.request.Request("https://api.telegram.org/bot%s/sendMessage" % t, data=data), timeout=15)
    try:
        sender(tok, chat, text); return True
    except Exception:
        return False


def run_from_scraper(today=None):
    """Called after the scraper has written all_deals.json. Report-only unless auto_apply is true."""
    cfg = load_cfg()
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if kill_switch_on(cfg):
        print("auto-update: kill switch on"); return
    state_doc = json.loads(pol.STATE_PATH.read_text(encoding="utf-8")); state = state_doc["offers"]
    deals = json.loads((ROOT / "all_deals.json").read_text(encoding="utf-8")).get("deals", [])
    amounts = {}
    for d in deals:
        amounts.setdefault(pol.key(d.get("store")), d.get("deal_price"))
    obs = []
    for k, rec in state.items():
        if refusal(k, rec) or rec.get("status") == "ended":
            continue
        cur = (rec.get("amount_override") or {}).get("value") or amounts.get(k)
        if cur:
            obs.append(fetch_observation(k, rec, cur))
    changes = plan(obs, state, {k: ((state[k].get("amount_override") or {}).get("value") or v) for k, v in amounts.items() if k in state}, cfg, today)
    log_path = ROOT / cfg["log_path"]
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    applied, queued, notes = apply(changes, state, cfg, "scraper", today, log)
    if applied:
        pol.STATE_PATH.write_text(json.dumps(state_doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        log_path.write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    qp = ROOT / cfg["queue_path"]
    qp.write_text(json.dumps(queued, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if cfg.get("digest", {}).get("telegram"):
        marker = ROOT / "config" / "autoupdate_digest.json"
        last = json.loads(marker.read_text(encoding="utf-8")).get("last_digest", "") if marker.exists() else ""
        if not (cfg["digest"].get("once_per_day") and last == today):
            if send_digest(digest_text(today, changes, applied, queued, notes)):
                marker.write_text(json.dumps({"last_digest": today}) + "\n", encoding="utf-8")
    print("auto-update: {} proposed, {} applied, {} queued. {}".format(len(changes), len(applied), len(queued), "; ".join(notes)))


if __name__ == "__main__":
    if "--revert" in sys.argv:
        rid = sys.argv[sys.argv.index("--revert") + 1]
        cfg = load_cfg(); lp = ROOT / cfg["log_path"]
        doc = json.loads(pol.STATE_PATH.read_text(encoding="utf-8")); log = json.loads(lp.read_text(encoding="utf-8"))
        n = revert(rid, doc["offers"], log)
        pol.STATE_PATH.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        lp.write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("reverted", n, "changes from run", rid)
    else:
        run_from_scraper()
