"""Old pages that moved must redirect and point their canonical at the new page.
Run: python3 tests/check_redirects.py"""
import os,sys
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
fail=[]
CHECKS={"game/index.html":"https://moneyhunters.co.uk/play/","guides/free-share-offers/index.html":"https://moneyhunters.co.uk/guides/share-bonus-offers/"}
for f,target in CHECKS.items():
    t=open(os.path.join(root,f),encoding="utf-8").read()
    if 'rel="canonical" href="%s"'%target not in t:fail.append(f+": canonical should be "+target)
    if 'http-equiv="refresh"' not in t:fail.append(f+": no meta refresh redirect")
    if "user-scalable=no" in t or "maximum-scale" in t:fail.append(f+": zoom is locked")
if fail:print("FAIL");print(*fail,sep="\n");sys.exit(1)
print("Redirect checks passed (%d moved pages)"%len(CHECKS))
