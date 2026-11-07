const {setup}=require('./lib.js');const fs=require('fs');
(async()=>{const save=fs.readFileSync(__dirname+'/base_save.json','utf8');const {b,p}=await setup({save});await p.click('#cont');await p.waitForTimeout(800);
for(const k of ['pete','captain','twins','carl','taxman','phisher','grimsby']){
 await p.evaluate(k=>{S.flags.firstBattle=true;bossFight(k)},k);await p.waitForFunction(()=>mode==='battle');await p.waitForTimeout(2200);
 const c=await p.evaluate(()=>{const cs=[...document.querySelectorAll('canvas')].filter(c=>c.offsetParent);const c=cs.sort((a,b)=>b.width*b.height-a.width*a.height)[0];const r=c.getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height}});
 await p.screenshot({path:__dirname+`/spr_${k}.png`,clip:{x:c.x+c.w*0.52,y:c.y+c.h*0.18,width:c.w*0.42,height:c.h*0.78}});
 await p.evaluate(()=>{mode='world';});await p.reload();await p.click('#cont').catch(()=>{});await p.waitForTimeout(700);
}
await b.close()})();
