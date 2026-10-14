"""Question bank checks: ids unique, answers valid, learn_more exists, game copy in sync with data/questions."""
import json,re,os,sys
root=os.path.join(os.path.dirname(__file__),'..')
qd=os.path.join(root,'data','questions');idx=json.load(open(os.path.join(qd,'index.json')))
pb=json.load(open(os.path.join(root,'data','playbook.json')))
art={a['id'] for c in pb['chapters'] for a in c['articles']}
errs=[];seen=set();allq=[]
for t,f in idx['files'].items():
    qs=json.load(open(os.path.join(qd,f)))['questions']
    if idx['counts'].get(t)!=len(qs):errs.append(f'{t}: index count {idx["counts"].get(t)} != {len(qs)}')
    for q in qs:
        allq.append(q)
        if q['id'] in seen:errs.append('duplicate id '+q['id'])
        seen.add(q['id'])
        if q.get('type','mc')=='mc':
            if len(q['options'])<2 or not(0<=q['answer']<len(q['options'])):errs.append('bad answer '+q['id'])
            if len(set(q['options']))!=len(q['options']):errs.append('duplicate options '+q['id'])
        if q.get('learn_more') and q['learn_more'] not in art and not q['learn_more'].startswith('guide-'):errs.append(f"{q['id']}: unknown learn_more {q['learn_more']}")
        if q.get('volatile') and not q.get('review_by'):errs.append('volatile without review_by '+q['id'])
s=open(os.path.join(root,'play','index.html'),encoding='utf-8').read()
qb=json.loads(re.search(r'<script id="qbank" type="application/json">(.*?)</script>',s,re.S).group(1).replace('<\\/','</'))
if [q['id'] for q in qb['questions']]!=[q['id'] for q in allq]:errs.append('game question bank out of sync: run python3 scripts/sync_qbank.py')
if errs:
    print('\n'.join(errs[:20]));sys.exit(1)
print(f'Question checks passed: {len(allq)} questions, game bank in sync.')
