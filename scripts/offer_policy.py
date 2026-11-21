"""Display rules for offers, shared by the offers.html generator, the register and the tests.
The app (app.html) has a JavaScript copy of the same rules; tests/offer_policy_cases.json is run
against both so they cannot drift apart.

Rules (Alberto, 20 Nov 2026):
- Investing (yes or borderline): show an "up to" amount only if the provider's own page states a maximum
  (max_claim with source_url and date). Otherwise show the reward type and "value varies", no £ figure.
- Premier amounts show only with the provider's eligibility conditions, otherwise the amount is hidden.
- Non-investing: keep the amount. Say "last checked <date> · provider page" only if source_url is the
  provider's own page AND last_checked came from a real fetch that matched. Otherwise "not verified by a person".
- No "free" wording about offers or rewards.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "data" / "offer_state.json"

# Leveraged / CFD brokers are never listed. IG is live only as a 'Share dealing account' (confirmed by Alberto, 21 Nov 2026).
HIDDEN_PROVIDERS = {"etoro", "xtb", "trading212", "trading212cfd"}

RISK_WARNING = ("Capital at risk. The value of investments can fall as well as rise and you may get back less "
                "than you put in. Nothing here is advice or a personal recommendation. Check the firm on the FCA register.")

_FREE_RULES = [
    (r"\bfree\s+shares?\b", "share bonus"),
    (r"\bfree\s+money\b", "bonus"),
    (r"(£[\d,]+(?:\.\d+)?)\s+free\b", r"\1 bonus"),
    (r"(\d+\s+months?)\s+free\b", r"\1 fee waiver"),
    (r"\bfree\s+national\s+trust\s+day\s+pass\b", "National Trust day pass offer"),
    (r"\bfree\s+(coffee|cake|transfer|card)\b", r"\1 offer"),
    (r"\brisk[- ]free\b", "lower-risk"),
    (r"\bfree\b", "no-charge"),
    (r"\bguaranteed\b", "possible"),
]
_FREE_RX = [(re.compile(a, re.I), b) for a, b in _FREE_RULES]


def plain(text):
    text = str(text or "")
    for rx, rep in _FREE_RX:
        text = rx.sub(rep, text)
    return text


def key(name):
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())


def is_hidden_provider(name):
    k = key(name)
    return k in HIDDEN_PROVIDERS or k.startswith(("etoro", "xtb", "trading212"))


def load_state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))["offers"] if STATE_PATH.exists() else {}


def state_for(state, name):
    k = key(name)
    if k in state:
        return state[k]
    for sk, sv in state.items():
        if len(k) >= 4 and (k.startswith(sk) or sk.startswith(k)):
            return sv
    return {}


def is_investing(st):
    return st.get("investing") in ("yes", "borderline")


def is_premier(text):
    return bool(re.search(r"premier", str(text or ""), re.I))


def verified_by_fetch(st):
    return bool(st.get("source_is_provider_page") and st.get("source_url") and st.get("last_checked")
                and st.get("checked_by") == "fetch")


def verification_label(st):
    if verified_by_fetch(st):
        return "last checked {} · provider page".format(st["last_checked"])
    return "not verified by a person"


def max_claim_ok(st):
    mc = st.get("max_claim") or {}
    return bool(mc.get("amount") and mc.get("source_url") and mc.get("date"))


def display_amount(st, raw_amount, text=""):
    """Return (amount_text, note). raw_amount is what the scraper or app holds."""
    raw_amount = str(raw_amount or "")
    ov = (st.get("amount_override") or {}).get("value")
    if ov and not is_investing(st):
        raw_amount = str(ov)  # amount read from the provider's own page by the scraper check (auto-update)
    if is_investing(st):
        if max_claim_ok(st):
            mc = st["max_claim"]
            return "up to {}".format(mc["amount"]), "provider page, {}".format(mc["date"])
        # only "shares" is named: it is explicit in the listing. Other reward types are unconfirmed guesses.
        rt = "Share bonus" if st.get("reward_type") == "shares" else "Sign-up reward"
        return rt + ", value varies", "no figure shown until the provider's page states a maximum"
    if raw_amount.strip().lower() in ("free", "free!"):
        return "Offer, conditions apply", ""
    if is_premier(text) and not st.get("conditions"):
        return "Premier account (amount hidden)", "eligibility conditions not confirmed"
    return raw_amount, ""
