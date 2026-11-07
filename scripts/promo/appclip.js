const {setup,startRec}=require('./lib.js');const {prep,tap}=require('./drive.js');const fs=require('fs');
const clickText=async(p,t,exact=true)=>{const h=await p.evaluateHandle(([t,e])=>{const m=[...document.querySelectorAll('button,a,[role=tab],summary,div,span,h3,h4')].filter(x=>x.offsetParent&&(e?x.innerText.trim()===t:x.innerText.trim().includes(t)));m.sort((a,b)=>a.getBoundingClientRect().width*a.getBoundingClientRect().height-b.getBoundingClientRect().width*b.getBoundingClientRect().height);return m[0]},[t,exact]);const el=h.asElement();if(!el){console.log('miss',t);return false}await tap(p,el,0);return true};
(async()=>{const {b,c,p}=await setup();
await c.route('**/cdn.jsdelivr.net/npm/@supabase/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/sb/node_modules/@supabase/supabase-js/dist/umd/supabase.js','utf8')}));
await c.route('**/*.supabase.co/**',r=>r.fulfill({status:200,contentType:'application/json',body:'[]'}));
await p.goto('http://localhost:8766/app.html');await p.waitForTimeout(2500);await prep(p);
await clickText(p,'Skip intro');await p.waitForTimeout(800);
// A: walkthrough
let r=await startRec(p,__dirname+'/ap_walk');await p.waitForTimeout(1800);
await clickText(p,'Offers');r.mark('offers');await p.waitForTimeout(1600);
await clickText(p,'🏦 Bank');r.mark('bank');await p.waitForTimeout(1500);
for(let i=0;i<5;i++){await p.mouse.wheel(0,260);await p.waitForTimeout(450);}
await p.mouse.wheel(0,-1300);await p.waitForTimeout(900);
const ok=await clickText(p,'First Direct',false);console.log('fd',ok);r.mark('expand');await p.waitForTimeout(2600);
for(let i=0;i<4;i++){await p.mouse.wheel(0,280);await p.waitForTimeout(600);}
r.mark('guide');await p.waitForTimeout(1500);
await clickText(p,'Play');r.mark('play');await p.waitForTimeout(2600);r.mark('endcard');await p.waitForTimeout(3600);
console.log(JSON.stringify((await r.stop()).marks));
// B: bank list short segment for bridge
await clickText(p,'Offers');await p.waitForTimeout(800);await p.evaluate(()=>scrollTo(0,0));
r=await startRec(p,__dirname+'/ap_bank');await p.waitForTimeout(800);await clickText(p,'🏦 Bank');await p.waitForTimeout(1200);
for(let i=0;i<4;i++){await p.mouse.wheel(0,240);await p.waitForTimeout(500);}await p.waitForTimeout(800);
console.log(JSON.stringify(await r.stop()));await b.close()})();
