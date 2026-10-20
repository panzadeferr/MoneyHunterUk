"""Guide pages must be built from data/playbook.json and up to date.
Run: python3 tests/check_guides.py"""
import subprocess,sys,tempfile,os,filecmp,json
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
fail=[]
tmp=tempfile.mkdtemp()
subprocess.run([sys.executable,os.path.join(root,"scripts","build_guide_pages.py"),"--out",tmp],check=True,capture_output=True)
def walk(base):
    r=set()
    for d,_,fs in os.walk(base):
        for f in fs:r.add(os.path.relpath(os.path.join(d,f),base))
    return r
a=walk(os.path.join(tmp,"guides"));b=walk(os.path.join(root,"guides")) if os.path.isdir(os.path.join(root,"guides")) else set()
if a!=b:fail.append("guide page set differs: missing %s extra %s"%(sorted(a-b)[:3],sorted(b-a)[:3]))
for f in sorted(a&b):
    if not filecmp.cmp(os.path.join(tmp,"guides",f),os.path.join(root,"guides",f),shallow=False):fail.append("out of date: guides/"+f)
for f in sorted(b):
    t=open(os.path.join(root,"guides",f),encoding="utf-8").read()
    for need in ("<title>","rel=\"canonical\"","application/ld+json","<h1>"):
        if need not in t and not f=="index.html" or (f=="index.html" and need in("<title>","rel=\"canonical\"","<h1>") and need not in t):fail.append(f"guides/{f} missing {need}")
pb=json.load(open(os.path.join(root,"data","playbook.json"),encoding="utf-8"))
n=sum(1 for c in pb["chapters"] if not c.get("locked") for x in c["articles"] if x.get("body"))
if len(b)-1!=n:fail.append(f"expected {n} guide pages, found {len(b)-1}")
if fail:
    print("FAIL");print(*fail[:15],sep="\n");print("Fix: python3 scripts/build_guide_pages.py");sys.exit(1)
print(f"Guide page checks passed: {n} pages + hub, in sync with playbook.json")
