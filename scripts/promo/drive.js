const {setup,startRec,hold}=require('./lib.js');const fs=require('fs');
const TAPCSS=`.__tap{position:fixed;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:4px solid #fff;background:rgba(255,201,74,.45);pointer-events:none;z-index:99999;animation:__t .55s ease-out forwards}@keyframes __t{0%{transform:scale(.4);opacity:1}100%{transform:scale(1.4);opacity:0}}`;
async function prep(p){await p.addStyleTag({content:TAPCSS});}
async function tap(p,sel,pause=0){
  const el=typeof sel==='string'?await p.$(sel):sel; if(!el) return false;
  await el.scrollIntoViewIfNeeded().catch(()=>{});
  const bb=await el.boundingBox(); if(!bb) return false;
  await el.evaluate(e=>{const r=e.getBoundingClientRect();const d=document.createElement('div');d.className='__tap';d.style.left=(r.left+r.width/2)+'px';d.style.top=(r.top+r.height/2)+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),700)});
  await p.waitForTimeout(160); await el.click({force:true}).catch(()=>{}); if(pause) await p.waitForTimeout(pause); return true;
}
async function visBtns(p){return p.evaluate(()=>[...document.querySelectorAll('#bpanel button,#dialog button,#ov button')].filter(x=>x.offsetParent&&!x.disabled).map(x=>({id:x.id,t:x.innerText.trim().slice(0,24)})));}
// battle driver: plan = array of moves ('attack'|'investigate'); qThink ms before answering
async function fight(p,{rec,plan,think=2200,flagGap=650,read=1500,maxSteps=40,after=2500}){
  let mi=0;await p.waitForFunction(()=>mode==='battle',null,{timeout:8000});
  for(let s=0;s<maxSteps;s++){
    if(process.env.DBG)console.log('step',s,JSON.stringify(await visBtns(p)));
    const st=await p.evaluate(()=>({mode,ans:!!(typeof B!=='undefined'&&B&&B.answering),inv:!!(typeof B!=='undefined'&&B&&B.answering&&B.q&&B.q.parts)}));
    if(st.mode!=='battle'){rec&&rec.mark('end');await p.waitForTimeout(after);return;}
    if(st.ans&&!st.inv){rec&&rec.mark('q'+(mi));await p.waitForTimeout(think);const k=await p.evaluate(()=>B.q.a);await tap(p,`#bpanel .opts button[data-k="${k}"]`,read+800);continue;}
    if(st.inv){rec&&rec.mark('inv'+(mi));await p.waitForTimeout(900);const idx=await p.evaluate(()=>B.q.parts.map((x,i)=>x.f&&!B.sel.has(i)?i:-1).filter(i=>i>=0));
      for(const i of idx){await tap(p,`.seg[data-i="${i}"]`,flagGap);} await p.waitForTimeout(300);await tap(p,'#check',read+900);continue;}
    const v=await visBtns(p);const ids=v.map(x=>x.id);
    if(ids.includes('mAtk')){const m=plan[Math.min(mi++,plan.length-1)];await p.waitForTimeout(700);await tap(p,m==='investigate'?'#mInv':'#mAtk',300);continue;}
    if(ids.includes('bshare'))rec&&rec.mark('win');
    const nxt=v.find(x=>x.id&&!['bshare','tBook','t5050','reset','mute'].includes(x.id));
    if(nxt){await p.waitForTimeout(read);await tap(p,'#'+nxt.id,500);continue;}
    await p.waitForTimeout(400);
  }
}
async function walk(p,seq){for(const [k,ms] of seq){await hold(p,k,ms);}}
module.exports={prep,tap,fight,walk,visBtns};
