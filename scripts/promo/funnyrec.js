const {setup,startRec,hold}=require('./lib.js');const {prep,tap,walk}=require('./drive.js');const fs=require('fs');
(async()=>{const L=JSON.parse(fs.readFileSync(__dirname+'/funnylist.json'));const save=fs.readFileSync(__dirname+'/base_save.json','utf8');
for(const [n,boss] of L){const {b,p}=await setup({save});await p.click('#cont').catch(()=>{});await p.waitForTimeout(800);await prep(p);
 await p.evaluate(()=>{S.flags.firstBattle=true;S.hp=maxHP();hud()});
 await walk(p,[['ArrowDown',1400]]);await p.waitForTimeout(300);
 const r=await startRec(p,__dirname+'/fr/'+n);
 await walk(p,[['ArrowRight',700],['ArrowDown',500]]);
 r.mark('boss');await p.evaluate(b=>bossFight(b),boss);await p.waitForFunction(()=>mode==='battle');
 await p.waitForSelector('#bgo',{state:'visible'});await p.waitForTimeout(2600);r.mark('taunt_end');
 await p.evaluate(()=>{B.e.hp=1});await tap(p,'#bgo',300);await p.waitForSelector('#mAtk',{state:'visible'});await p.waitForTimeout(300);await tap(p,'#mAtk',600);
 if(await p.evaluate(()=>!!B.q.parts)){const idx=await p.evaluate(()=>B.q.parts.map((x,i)=>x.f?i:-1).filter(i=>i>=0));for(const i of idx)await tap(p,`.seg[data-i="${i}"]`,250);await tap(p,'#check',0);}
 else{const k=await p.evaluate(()=>B.q.a);await tap(p,`#bpanel .opts button[data-k="${k}"]`,0);}
 r.mark('hit');
 // advance until victory text shows
 for(let i=0;i<10;i++){await p.waitForTimeout(900);const v=await p.evaluate(()=>[...document.querySelectorAll('#bpanel button')].filter(x=>x.offsetParent&&!x.disabled).map(x=>x.id));if(v.includes('bshare')){break;}const nx=v.find(x=>x&&!['bshare','tBook','t5050'].includes(x));if(nx)await tap(p,'#'+nx,0);}
 r.mark('win');await p.waitForTimeout(3200);r.mark('endcard');await p.waitForTimeout(3300);
 console.log(n,JSON.stringify((await r.stop()).marks));await b.close();}
})();
