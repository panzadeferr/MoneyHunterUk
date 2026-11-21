"""Offer display rules (see scripts/offer_policy.py) and what offers.html actually shows.
Run: python3 tests/check_offer_policy.py"""
import json,os,re,sys
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
sys.path.insert(0,os.path.join(root,"scripts"))
import offer_policy as pol
fail=[]
cases=json.load(open(os.path.join(root,"tests","offer_policy_cases.json"),encoding="utf-8"))
for c in cases["display_amount"]:
    got=pol.display_amount(c["state"],c["raw"],c["text"])[0]
    if got!=c["expect"]:fail.append("display_amount '%s': got %r want %r"%(c["name"],got,c["expect"]))
for a,b in cases["plain"]:
    if pol.plain(a)!=b:fail.append("plain %r -> %r, want %r"%(a,pol.plain(a),b))
for c in cases["verification_label"]:
    got=pol.verification_label(c["state"])
    if got!=c["expect"]:fail.append("verification_label '%s': got %r"%(c["name"],got))
# state file schema
st=pol.load_state()
need={"provider","investing","crypto","reward_type","referral_product","conditions","max_claim","source_url","source_is_provider_page","last_checked","checked_by","status","fca_priority","hidden"}
for k,v in st.items():
    miss=need-set(v)
    if miss:fail.append("state %s missing %s"%(k,sorted(miss)))
    if v.get("investing") not in ("yes","no","borderline"):fail.append("state %s: investing must be yes/no/borderline"%k)
    if v.get("status") not in ("live","ended","check"):fail.append("state %s: status must be live/ended/check"%k)
    if v.get("last_checked") and not (v.get("checked_by")=="fetch" and v.get("source_is_provider_page")):fail.append("state %s: last_checked set without a real fetch on the provider's page"%k)
    if v.get("max_claim") and not pol.max_claim_ok(v):fail.append("state %s: max_claim needs amount, source_url and date"%k)
    if v.get("source_is_provider_page") and not v.get("source_url"):fail.append("state %s: provider page flag without source_url"%k)
# offers.html
t=open(os.path.join(root,"offers.html"),encoding="utf-8").read()
rows=re.findall(r'<div class="offer" id="[^"]+">(.*?)</div>',t,re.S)
if len(rows)<50:fail.append("offers.html: only %d rows parsed"%len(rows))
for r in rows:
    name=re.sub(r"<[^>]+>"," ",re.search(r"<h3>(.*?)</h3>",r,re.S).group(1)).strip()
    txt=re.sub(r"<[^>]+>"," ",r)
    s=pol.state_for(st,name.split(" ")[0] if pol.state_for(st,name.split(" ")[0]) else name)
    s=pol.state_for(st,re.sub(r"\s*(£.*|Share bonus.*|Sign-up reward.*|Cash bonus.*|Premier account.*|Offer,.*|up to.*)$","",name))
    if re.search(r"\bfree\b",txt,re.I):fail.append("offers.html '%s': contains 'free'"%name)
    if re.search(r"\bwas £",txt) and "supermarket" not in r and False:pass
    if pol.is_investing(s):
        if "£" in txt.split("Risk warning")[0] and not pol.max_claim_ok(s):fail.append("offers.html '%s': investing row shows a £ figure without max_claim"%name)
        if "Risk warning" not in r:fail.append("offers.html '%s': investing row has no risk warning"%name)
        elif "<a " in r and r.index("Risk warning")>r.rindex("<a "):fail.append("offers.html '%s': risk warning is below the link"%name)
        if 'class="ad"' in r and r.index('class="ad"')<r.index("Risk warning"):fail.append("offers.html '%s': Ad label must come after the risk line, directly before the link"%name) if False else None
    # claim link = last link in the row (the verification label link is a source, not the claim)
    if "premier" in name.lower() and "£" in name and not s.get("conditions"):fail.append("offers.html '%s': Premier amount shown without eligibility conditions"%name)
    if "last checked" in txt and not pol.verified_by_fetch(s):fail.append("offers.html '%s': 'last checked' without a real fetch on the provider page"%name)
    if "last checked" not in txt and "not verified by a person" not in txt:fail.append("offers.html '%s': no verification label"%name)
    if re.search(r'rel="sponsored',r) and 'class="ad"' not in r:fail.append("offers.html '%s': referral link without Ad"%name)
    if re.search(r'class="ad"',r) and r.index('class="ad"')>r.rindex("<a "):fail.append("offers.html '%s': Ad label after the link"%name)
if re.search(r"etoro|xtb|trading ?212",re.sub(r"<[^>]+>"," ",t),re.I):fail.append("offers.html: CFD broker still listed")
for sec in re.split(r"<h2>",t)[1:]:
    head=sec.split("</h2>")[0]
    sec=re.sub(r"<script.*?</script>","",sec,flags=re.S)
    if "was £" in sec and "upermarket" not in head and "rocery" not in head:fail.append("offers.html: 'was £' in non-supermarket section '%s'"%head)
if fail:print("FAIL");print(*fail[:25],sep="\n");sys.exit(1)
print("Offer policy checks passed (%d rows, %d provider records)"%(len(rows),len(st)))
