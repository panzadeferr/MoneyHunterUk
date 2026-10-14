"""Rebuild the game's embedded question bank from data/questions/*.json and refresh index.json counts.
Run after adding questions: python3 scripts/sync_qbank.py"""
import json,re,os,datetime
root=os.path.join(os.path.dirname(__file__),'..')
qd=os.path.join(root,'data','questions')
idx=json.load(open(os.path.join(qd,'index.json')))
files=dict(idx['files']);
for f in sorted(os.listdir(qd)):
    if f.endswith('.json') and f not in('index.json','investigations.json'):
        t=f[:-5]
        if t not in files:files[t]=f
questions=[];counts={}
for t,f in files.items():
    qs=json.load(open(os.path.join(qd,f)))['questions'];questions+=qs;counts[t]=len(qs)
idx['files']=files;idx['counts']=counts;idx['batch']=3;idx['updated']=datetime.date.today().isoformat()
open(os.path.join(qd,'index.json'),'w').write(json.dumps(idx))
gp=os.path.join(root,'play','index.html');s=open(gp,encoding='utf-8').read()
m=re.search(r'(<script id="qbank" type="application/json">)(.*?)(</script>)',s,re.S)
qb=json.loads(m.group(2));qb['questions']=questions;qb['batch']=3;qb['updated']=idx['updated']
s=s[:m.start(2)]+json.dumps(qb,ensure_ascii=False).replace('</','<\\/')+s[m.end(2):]
# make sure rent guides are known to the game
pb=json.load(open(os.path.join(root,'data','playbook.json')))
m=re.search(r'(<script id="guides" type="application/json">)(.*?)(</script>)',s,re.S);g=json.loads(m.group(2))
for c in pb['chapters']:
    if c.get('locked'):continue
    for a in c['articles']:
        if a['id'] not in g and a.get('body'):g[a['id']]={'t':a['title'],'s':a.get('summary',''),'tp':c['title']}
s=s[:m.start(2)]+json.dumps(g,ensure_ascii=False).replace('</','<\\/')+s[m.end(2):]
open(gp,'w',encoding='utf-8').write(s)
print(len(questions),'questions;',len(g),'guides')
