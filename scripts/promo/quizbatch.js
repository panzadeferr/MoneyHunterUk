const {setup,startRec}=require('./lib.js');const {prep,tap}=require('./drive.js');const ov=require('./override.js');const fs=require('fs');
(async()=>{const list=JSON.parse(fs.readFileSync(__dirname+'/quizlist.json','utf8'));const save=fs.readFileSync(__dirname+'/base_save.json','utf8');
for(const [name,qid,boss] of list){
 const {b,p}=await setup({save});
 await p.click('#cont').catch(()=>{});await p.waitForTimeout(800);await prep(p);
 await p.evaluate(()=>{S.flags.firstBattle=true;S.hp=maxHP();hud()});await p.evaluate(ov([qid]));
 await p.evaluate(b=>bossFight(b),boss);await p.waitForFunction(()=>mode==='battle');
 await p.waitForSelector('#bgo',{state:'visible'});await p.click('#bgo');await p.waitForSelector('#mAtk',{state:'visible'});
 const r=await startRec(p,__dirname+'/qb/'+name);
 await p.waitForTimeout(600);await tap(p,'#mAtk',200);r.mark('q');
 await p.waitForTimeout(6200);const k=await p.evaluate(()=>B.q.a);const got=await p.evaluate(()=>B.q.id);r.mark('ans');await tap(p,`#bpanel .opts button[data-k="${k}"]`,0);
 await p.waitForTimeout(5200);r.mark('endcard');await p.waitForTimeout(3600);
 const info=await r.stop();console.log(name,got,JSON.stringify(info.marks));await b.close();}
})();
