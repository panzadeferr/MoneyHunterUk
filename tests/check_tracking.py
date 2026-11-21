"""Every page that loads Umami must first run the ?mh_me=1 opt-out snippet.
?mh_me=1 sets localStorage umami.disabled=1 (Umami's own opt-out flag), ?mh_me=0 clears it.
Run: python3 tests/check_tracking.py"""
import os,re,sys
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
fail=[];n=0
for d,dirs,fs in os.walk(root):
    dirs[:]=[x for x in dirs if x not in (".git","node_modules","__pycache__")]
    for f in fs:
        if not f.endswith(".html"):continue
        p=os.path.join(d,f);t=open(p,encoding="utf-8",errors="ignore").read()
        m=re.search(r'<script[^>]*src="https://cloud\.umami\.is/script\.js"',t)
        if not m:continue
        n+=1;rel=os.path.relpath(p,root)
        head=t[:m.start()]
        if "umami.disabled" not in head or "mh_me" not in head:fail.append(rel+": opt-out snippet missing before the Umami script")
        elif "'1'" not in head[head.rfind("mh_me")-5:]:fail.append(rel+": snippet does not set the flag")
for g in ("scripts/make_offers_page.py","scripts/build_guide_pages.py"):
    t=open(os.path.join(root,g),encoding="utf-8").read()
    if "umami.disabled" not in t:fail.append(g+": generator has no opt-out snippet")
if n<5:fail.append("expected Umami pages, found %d"%n)
if fail:print("FAIL");print(*fail[:15],sep="\n");sys.exit(1)
print("Tracking opt-out check passed (%d pages load Umami, all opt out first)"%n)
