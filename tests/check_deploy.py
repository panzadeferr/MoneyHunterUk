"""Every page the site links to must actually be published by the deploy.
Deploy copies an explicit file list (.github/workflows/deploy.yml), so a new page that is not on that
list returns 404 live even though tests pass (this happened to newsletter.html, 18 Nov 2026).
Checks: (1) every root *.html is on the list, (2) every sitemap URL is published,
(3) every local /page.html or /folder/ link in the public pages is published.
Run: python3 tests/check_deploy.py"""
import os,re,sys,fnmatch,glob
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
os.chdir(root)
wf=open(".github/workflows/deploy.yml",encoding="utf-8").read()
files=set();dirs=set();globs=set()
for line in wf.splitlines():
    s=line.strip()
    m=re.match(r"(?:\[ -d \S+ \] && )?cp (-r )?(.+?)(?: \|\| true)?$",s)
    if not m:continue
    toks=m.group(2).split()
    if m.group(1):
        toks=toks[:-1]  # last token is the destination
        for t in toks:dirs.add(t.rstrip("/").split("/")[0].replace("data/.","data"))
        continue
    toks=toks[:-1]
    for t in toks:
        if "/" in t:dirs.add(t.split("/")[0])  # e.g. play/index.html, shots/*.webp
        (globs if "*" in t else files).add(t)
def published(path):
    p=path.split("?")[0].split("#")[0].lstrip("/")
    if p in("","index.html"):return True
    if p.endswith("/") or "/" in p:
        return p.split("/")[0] in dirs
    return p in files or any(fnmatch.fnmatch(p,g) for g in globs)
fail=[]
for f in sorted(glob.glob("*.html")):
    if not published(f):fail.append(f"{f} is in the repo but not on the deploy copy list")
sm=open("sitemap.xml",encoding="utf-8").read()
for loc in re.findall(r"<loc>https://moneyhunters\.co\.uk(/[^<]*)</loc>",sm):
    if not published(loc):fail.append(f"sitemap lists {loc} but the deploy does not publish it")
for page in ["index.html","app.html","offers.html","bank-switch.html","privacy.html","newsletter.html"]:
    if not os.path.exists(page):continue
    t=open(page,encoding="utf-8").read()
    for h in set(re.findall(r'href="(/[a-zA-Z0-9_./-]*(?:\.html|/))(?:[?#"][^"]*)?"',t)):
        if not published(h):fail.append(f"{page} links to {h} which the deploy does not publish")
if fail:
    print("FAIL");print(*sorted(set(fail)),sep="\n");print("Fix: add the file or folder to the 'Build site folder' step in .github/workflows/deploy.yml");sys.exit(1)
print(f"Deploy list check passed: {len(files)} files, {len(dirs)} folders, sitemap and page links all published")
