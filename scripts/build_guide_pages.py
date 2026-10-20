"""Builds one static, searchable page per Playbook guide from data/playbook.json.
Output: guides/<slug>/index.html and guides/index.html. scripts/make_sitemap.py adds them to the sitemap at deploy.
Run: python3 scripts/build_guide_pages.py   (add --out DIR to build somewhere else, used by tests)"""
import json,os,re,sys,html,datetime
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
SITE="https://moneyhunters.co.uk"
out=ROOT
if "--out" in sys.argv: out=sys.argv[sys.argv.index("--out")+1]
E=lambda s:html.escape(str(s),quote=True)
def slugify(t):
    s=re.sub(r"[^a-z0-9]+","-",t.lower().replace("&","and").replace("£","")).strip("-")
    return s
def nice(d):
    y,m,dd=map(int,d.split("-"));return f"{dd} {datetime.date(y,m,dd).strftime('%B')} {y}"
pb=json.load(open(os.path.join(ROOT,"data","playbook.json"),encoding="utf-8"))
NEWS='<div class="box"><div class="lbl">Weekly email</div><p>The Money Drop: one email a week with the freshest UK bank switches, cashback and free-share offers. Free, unsubscribe any time.</p><iframe loading="lazy" title="Subscribe to the Money Drop" width="540" height="305" src="https://74f208ba.sibforms.com/v2/serve/MUIFAFatJ19YBCgL_8OC4uZ5fBePkhu7SoQvYgtr0wdDAHDh8p3INb8HL95eBukwXmcw6eSy9l21fAZ9j904cUItf6li832Ro_b8bIkYS6DRWodkrhDtEnh_e_Uby_2jvxs6ApPdjg9-KI3K69aSvIwTx7GL_JoR-9iAg5078QebcnjT28u-EKbYoAA6YamSH3UvqHQA_Nj4w9bvyw==" frameborder="0" scrolling="auto" style="display:block;max-width:100%;border:0"></iframe></div>'
UMAMI='<script defer src="https://cloud.umami.is/script.js" data-website-id="f9d2c068-643f-4cfc-847e-c22fec24bafe"></script>'
CSS="""
:root{--bg:#080b10;--bg2:#0d1219;--bg3:#131b26;--g:#1fe887;--gl:rgba(31,232,135,.12);--t:#f0f4f8;--tm:#a3b2c4;--tl:#6b7d92;--line:rgba(255,255,255,.08);--warn:#ffb454;--fh:'Inter',system-ui,sans-serif;--fb:'DM Sans',system-ui,sans-serif}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);font-family:var(--fb);color:var(--t);-webkit-font-smoothing:antialiased;line-height:1.7}
a{color:var(--g)}
.top{display:flex;gap:18px;align-items:center;flex-wrap:wrap;padding:16px 20px;border-bottom:1px solid var(--line);background:var(--bg2)}
.top .logo{font-family:var(--fh);font-weight:800;color:var(--t);text-decoration:none;margin-right:auto}
.top a{font-size:14px;text-decoration:none}
.wrap{max-width:720px;margin:0 auto;padding:32px 20px 64px}
.crumbs{font-size:13px;color:var(--tl);margin-bottom:14px}
.crumbs a{color:var(--tm)}
h1{font-family:var(--fh);font-size:clamp(26px,5vw,34px);font-weight:800;line-height:1.2;margin-bottom:10px}
.lede{font-size:17px;color:var(--tm);margin-bottom:10px}
.meta{font-size:13px;color:var(--tl);margin-bottom:28px}
h2{font-family:var(--fh);font-size:20px;font-weight:700;color:var(--g);margin:30px 0 10px}
p,li{font-size:16px;color:var(--tm);margin-bottom:10px}
ul,ol{padding-left:22px;margin-bottom:14px}
strong{color:var(--t)}
.box{border-radius:12px;padding:14px 18px;margin:18px 0;border:1px solid var(--line);background:var(--bg3)}
.box p,.box li{margin-bottom:6px}
.box .lbl{font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;margin-bottom:6px;color:var(--g)}
.box.warn{border-color:rgba(255,180,84,.35)}.box.warn .lbl{color:var(--warn)}
.cta{background:var(--gl);border:1px solid rgba(31,232,135,.3);border-radius:14px;padding:18px 20px;margin:34px 0}
.cta h2{margin-top:0}
.btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.btn{display:inline-block;padding:10px 16px;border-radius:10px;background:var(--g);color:#04130b;font-weight:700;text-decoration:none;font-size:15px}
.btn.alt{background:transparent;color:var(--g);border:1px solid var(--g)}
.src li{font-size:14px;word-break:break-word}
.rel a{display:block;padding:10px 0;border-bottom:1px solid var(--line);text-decoration:none}
.rel span{display:block;font-size:14px;color:var(--tl)}
.disc{font-size:13px;color:var(--tl);margin-top:30px;border-top:1px solid var(--line);padding-top:14px}
.ch h2{margin-top:26px}
"""
HEAD_FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">'
NAV='<div class="top"><a class="logo" href="/">Money Hunters UK</a><a href="/guides/">All guides</a><a href="/app.html">App</a><a href="/play/">Game</a></div>'
DISC='<p class="disc">This is general information, not financial advice. Offers and rules change, so check the provider\'s own terms before you act. Some links on Money Hunters UK are referral links; see our <a href="/privacy.html">privacy and affiliate disclosure</a>.</p>'
def render_body(body):
    o=[]
    for b in body:
        t=b["type"]
        if t=="p":o.append(f"<p>{E(b['text'])}</p>")
        elif t=="h":o.append(f"<h2>{E(b['text'])}</h2>")
        elif t=="list":o.append("<ul>"+"".join(f"<li>{E(i)}</li>" for i in b["items"])+"</ul>")
        elif t=="steps":o.append("<ol>"+"".join(f"<li>{E(i)}</li>" for i in b["items"])+"</ol>")
        elif t=="key":o.append('<div class="box"><div class="lbl">Key points</div><ul>'+"".join(f"<li>{E(i)}</li>" for i in b["items"])+"</ul></div>")
        elif t=="tip":o.append(f'<div class="box"><div class="lbl">Tip</div><p>{E(b["text"])}</p></div>')
        elif t=="warn":o.append(f'<div class="box warn"><div class="lbl">Watch out</div><p>{E(b["text"])}</p></div>')
        else:raise SystemExit("unknown block type "+t)
    return "\n".join(o)
chapters=[c for c in pb["chapters"] if not c.get("locked")]
slugs={};used=set();pages=[]
for c in chapters:
    for a in c["articles"]:
        if not a.get("body"):continue
        s=slugify(a["title"]);base=s;n=2
        while s in used:s=f"{base}-{n}";n+=1
        used.add(s);slugs[a["id"]]=s;pages.append((c,a,s))
def w(path,txt):
    full=os.path.join(out,path);os.makedirs(os.path.dirname(full),exist_ok=True);open(full,"w",encoding="utf-8").write(txt)
for c,a,s in pages:
    url=f"{SITE}/guides/{s}/"
    desc=a["summary"]
    ld=json.dumps({"@context":"https://schema.org","@type":"Article","headline":a["title"],"description":desc,"dateModified":a["reviewed"],"mainEntityOfPage":url,"author":{"@type":"Organization","name":"Money Hunters UK"},"publisher":{"@type":"Organization","name":"Money Hunters UK"}},ensure_ascii=False)
    rel=[x for x in c["articles"] if x["id"]!=a["id"] and x.get("body")][:4]
    relhtml="".join(f'<a href="/guides/{slugs[x["id"]]}/">{E(x["title"])}<span>{E(x["summary"])}</span></a>' for x in rel)
    srcs="".join(f'<li><a href="{E(u)}" rel="noopener" target="_blank">{E(re.sub(r"^https?://(www\.)?","",u))}</a></li>' for u in a.get("sources",[]))
    qn=a.get("question_count") or 0
    PRACTICE=(f"There are {qn} practice questions on this topic in the free Coinsworth game. " if qn else "Test yourself with short questions in the free Coinsworth game. ")+"Or open this guide in the app to see live offers and tools."
    page=f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(a['title'])} | Money Hunters UK</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#080b10">
<meta property="og:type" content="article">
<meta property="og:title" content="{E(a['title'])}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<link rel="icon" type="image/png" href="/icon-192.png">
{HEAD_FONTS}
<style>{CSS}</style>
<script type="application/ld+json">{ld}</script>
{UMAMI}
</head>
<body>
{NAV}
<main class="wrap">
<p class="crumbs"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {E(c['title'])}</p>
<h1>{E(a['title'])}</h1>
<p class="lede">{E(desc)}</p>
<p class="meta">{E(c['title'])} · {a['read_minutes']} min read · Last reviewed {nice(a['reviewed'])}</p>
{render_body(a['body'])}
<div class="cta"><h2>Put it into practice</h2><p>{PRACTICE}</p><div class="btns"><a class="btn" href="/play/?utm_source=guide&amp;utm_medium={E(s)}">Play the game</a><a class="btn alt" href="/app.html?guide={E(a['id'])}">Open in the app</a></div></div>
<h2>Sources</h2>
<ul class="src">{srcs}</ul>
{NEWS}
<h2>More in {E(c['title'])}</h2>
<div class="rel">{relhtml or '<p>More guides are on the <a href="/guides/">guides page</a>.</p>'}</div>
{DISC}
</main>
</body>
</html>
"""
    w(f"guides/{s}/index.html",page)
# hub
sec=""
for c in chapters:
    items="".join(f'<a href="/guides/{slugs[a["id"]]}/">{E(a["title"])}<span>{E(a["summary"])}</span></a>' for a in c["articles"] if a.get("body"))
    if items:sec+=f'<div class="ch"><h2>{c.get("icon","")} {E(c["title"])}</h2><div class="rel">{items}</div></div>'
hub=f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UK Money Guides: banking, cashback, tax, renting and more | Money Hunters UK</title>
<meta name="description" content="Free, sourced UK money guides: bank switching, cashback, saving, tax, renting, credit and scams. Each guide shows when it was last reviewed.">
<link rel="canonical" href="{SITE}/guides/">
<meta name="theme-color" content="#080b10">
<link rel="icon" type="image/png" href="/icon-192.png">
{HEAD_FONTS}
<style>{CSS}</style>
{UMAMI}
</head>
<body>
{NAV}
<main class="wrap">
<h1>UK money guides</h1>
<p class="lede">Plain-English guides with their sources and the date they were last reviewed. Learn first, then pick what is worth your time.</p>
{sec}
{DISC}
</main>
</body>
</html>
"""
w("guides/index.html",hub)
print(f"built {len(pages)} guide pages + hub")
