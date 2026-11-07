import re,sys,json
# multi.py out_dir spec.json -> writes out_dir/list.txt ; prints segment start offsets
out,spec=sys.argv[1],json.load(open(sys.argv[2]))
import os;os.makedirs(out,exist_ok=True)
lines=[];t=0;starts=[]
for seg in spec:
    L=open(seg['dir']+'/list.txt').read()
    ents=re.findall(r"file '([^']+)'\nduration ([\d.]+)",L)
    a,b=seg.get('from',0),seg.get('to',1e9)
    starts.append(round(t,2));c=0
    for f,d in ents:
        d=float(d)
        if c+d>a and c<b:
            dd=min(c+d,b)-max(c,a);lines.append(f"file '{f}'\nduration {dd:.4f}");t+=dd
        c+=d
hold=spec[-1].get('hold',0)
if hold:
    f=re.findall(r"file '([^']+)'",lines[-1])[0];lines.append(f"file '{f}'\nduration {hold}");t+=hold
lines.append(lines[-1].split('\n')[0])
open(out+'/list.txt','w').write('\n'.join(lines)+'\n')
print(json.dumps({'starts':starts,'total':round(t,2)}))
