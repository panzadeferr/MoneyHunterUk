"""Partner ad slots (Trading.com): switched OFF by default and invisible when off.
OFF (repo state): data/partner-slots.json is empty, no partner page, and no deployable file mentions the partner.
ON  (simulated in a temp dir): the slot is labelled Ad, carries a risk warning and the two event names,
no link is present until a referral URL is supplied, the draft page is noindex, and no leveraged-product wording appears.
Run: python3 tests/check_partner_slots.py"""
import json,os,re,subprocess,sys,tempfile
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
fail=[]
flags=json.load(open(os.path.join(root,"config","feature_flags.json")))
if flags.get("TRADING_COM_ENABLED") is not False:
    print("NOTE: TRADING_COM_ENABLED is on; skipping the OFF-state checks")
else:
    sl=json.load(open(os.path.join(root,"data","partner-slots.json")))
    if sl!={"slots":[]}:fail.append("OFF: data/partner-slots.json is not empty")
    if os.path.exists(os.path.join(root,"guides","trading-com-invest-account")):fail.append("OFF: partner guide page exists")
    rx=re.compile(r"trading\.com|trading-com|tradingcom|trading_com",re.I)
    skip={".git","node_modules","__pycache__","config","partners","tests","scripts","docs","game","memory_bank.md"}
    for d,dirs,fs in os.walk(root):
        dirs[:]=[x for x in dirs if x not in skip and not (d==root and x in {"docs","game"})]
        for f in fs:
            if not f.endswith((".html",".json",".xml",".js",".txt",".webmanifest")):continue
            if d==root and f in ("memory_bank.md",):continue
            p=os.path.join(d,f)
            if rx.search(open(p,encoding="utf-8",errors="ignore").read()):fail.append("OFF: partner mentioned in "+os.path.relpath(p,root))
# data/partner-slots.json must match what the flags produce
t0=tempfile.mkdtemp()
subprocess.run([sys.executable,os.path.join(root,"scripts","build_partner_slots.py"),"--out",t0],check=True,capture_output=True)
if json.load(open(os.path.join(t0,"data","partner-slots.json")))!=json.load(open(os.path.join(root,"data","partner-slots.json"))):
    fail.append("data/partner-slots.json is out of date: run python3 scripts/build_partner_slots.py")
# ON state
tmp=tempfile.mkdtemp()
env=dict(os.environ,MH_FORCE_PARTNERS="trading-com")
subprocess.run([sys.executable,os.path.join(root,"scripts","build_partner_slots.py"),"--out",tmp],check=True,capture_output=True,env=env)
subprocess.run([sys.executable,os.path.join(root,"scripts","build_guide_pages.py"),"--out",tmp],check=True,capture_output=True,env=env)
on=json.load(open(os.path.join(tmp,"data","partner-slots.json")))["slots"]
if len(on)!=1:fail.append("ON: expected one slot, got %d"%len(on))
else:
    s=on[0];blob=json.dumps(s).lower()
    if s["ad_label"]!="Ad":fail.append("ON: slot is not labelled Ad")
    if "capital at risk" not in s["risk"].lower():fail.append("ON: no capital at risk warning")
    if "fca register" not in s["risk"].lower():fail.append("ON: no FCA register line")
    if s["events"]!={"view":"trading-com-view","click":"trading-com-click"}:fail.append("ON: event names wrong")
    if s["url"]:fail.append("ON: a link is set; add one only when the approved referral URL is supplied")
    for bad in ("cfd","leverag","spread bet","guarantee","risk-free","free money","return","earn","limited time","hurry","now!","£"):
        if bad in blob:fail.append("ON: slot wording contains '%s'"%bad)
pg=os.path.join(tmp,"guides","trading-com-invest-account","index.html")
if not os.path.exists(pg):fail.append("ON: draft page not built")
else:
    t=open(pg,encoding="utf-8").read();tl=t.lower()
    if 'name="robots" content="noindex"' not in t:fail.append("ON: draft page is indexable")
    if "<strong>Ad.</strong>" not in t:fail.append("ON: page has no Ad label")
    if "capital at risk" not in tl:fail.append("ON: page has no capital at risk")
    for bad in ("cfd","leverag","spread bet","guarantee","risk-free","free money"):
        if bad in tl:fail.append("ON: page contains '%s'"%bad)
    if "umami.disabled" not in t:fail.append("ON: page missing analytics opt-out")
if fail:print("FAIL");print(*fail[:20],sep="\n");sys.exit(1)
print("Partner slot checks passed (OFF: nothing published; ON: Ad label, risk warning, events, no link, draft noindex)")
