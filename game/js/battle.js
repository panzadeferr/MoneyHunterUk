// battle.js: side-on quiz battles with wallets, investigate mode, statuses, two-phase bosses.
let B=null;
const fx={shake:0,flash:0,phit:0,pops:[],parts:[],anim:null,eDisp:0,pDisp:0,banner:0,kb:0,pkb:0,dead:1};
function startBattle(kind,e){
  trans={kind:"flash",t:0,dur:700,cb:()=>{
    mode="battle";B={kind,e,streak:0,shield:false,counter:false,dazed:false,used:new Set(),free5050:isCls("scholar"),answering:false};
    Object.assign(fx,{shake:0,flash:0,phit:0,pops:[],parts:[],anim:null,eDisp:e.hp||0,pDisp:S.hp,banner:kind==="boss"?1600:0,kb:0,pkb:0,dead:1,intro:0});
    $("controls").hidden=true;$("bpanel").hidden=false;
    if(kind==="boss"){SFX.alert();bp(`<p class="btext">...</p>`);setTimeout(bIntro,1600)}else bIntro();
  }};
}
function markSeen(id,inv){B.used.add(id);const arr=inv?S.seenInv:S.seen;if(!arr.includes(id))arr.push(id)}
function pickQ(type){
  if(type==="inv"&&!INV.length)return pickQ("normal");
  if(!QS.length)return{id:"boot",tag:"general",tier:1,t:"mc",q:"The question bank is still loading. Try again in a moment.",o:["OK"],a:0,e:"Questions load from /data/. If this keeps appearing, the data files are missing.",learn:""};
  if(type==="inv"){let p=INV.filter(q=>!B.used.has(q.id)&&!S.seenInv.includes(q.id));if(!p.length){S.seenInv=[];p=INV.filter(q=>!B.used.has(q.id))}if(!p.length)p=INV;const q=pick(p);markSeen(q.id,true);return q}
  const tags=B.kind==="offer"?[B.e.tag]:B.e.tags,tier=type==="easy"?Math.max(1,B.e.tier-1):B.e.tier,lo=tier>=3?2:1,hi=tier;
  const elig=QS.filter(q=>tags.includes(q.tag)&&q.tier>=lo&&q.tier<=hi);
  let p=elig.filter(q=>!B.used.has(q.id)&&!S.seen.includes(q.id));
  if(!p.length){const wide=QS.filter(q=>q.tier>=lo&&q.tier<=hi);p=wide.filter(q=>!B.used.has(q.id)&&!S.seen.includes(q.id));
    if(!p.length){const ids=new Set(wide.map(q=>q.id));S.seen=S.seen.filter(id=>!ids.has(id));p=elig.filter(q=>!B.used.has(q.id))}}
  if(!p.length)p=QS.filter(q=>!B.used.has(q.id)&&q.tier<=hi);
  if(!p.length)p=QS;
  const q=pick(p);markSeen(q.id,false);return q;
}
function bIntro(){
  const e=B.e;let t,tip="";
  if(B.kind==="boss")t=`<strong>${e.n.toUpperCase()}</strong>: “${e.taunt}”`;
  else if(B.kind==="offer")t=`Something shiny is rustling in the grass... it's a <strong>${e.n.toUpperCase()}</strong> Wild Offer! Answer its question to catch it.`;
  else t=`<strong>${e.n.toUpperCase()}</strong> blocks your path!`;
  if(e.weak&&S.notes[e.n])tip+=`<p class="tip">Penny's notes: weak to <b>${e.weak.toUpperCase()}</b>.</p>`;
  if(!S.flags.firstBattle&&B.kind!=="offer"){S.flags.firstBattle=true;tip+=`<p class="tip">How battles work: pick a move, then answer its question. A right answer powers the move. Then the enemy hits back. Every answer comes with an explanation, so you learn either way.</p>`}
  bp(`<p class="btext">${t}</p>${tip}<button class="go wide" id="bgo">CONTINUE</button>`);on("bgo",()=>{SFX.tap();bMenu()});$("bgo").focus();
}
function bMenu(){
  finishAnim();B.answering=false;
  if(B.kind==="offer"){bp(`<p class="btext">What will you do?</p><div class="moves"><button class="mv inv" id="mCatch"><strong>CATCH</strong><span>Answer right to add this card to your collection</span></button><button class="mv" id="mRun"><strong>RUN</strong><span>Let it go</span></button></div>`);on("mCatch",()=>bAsk("catch"));on("mRun",bRun);return}
  const pots=(S.items.potion||0)+(S.items.superpotion||0);
  bp(`<p class="btext">What will you do?${B.streak>=2?` <span class="hint">Streak ×${B.streak}</span>`:""}${B.dazed?` <span class="bad">· DAZED: half time next question</span>`:""}</p>
    <div class="moves">
      <button class="mv atk" id="mAtk"><strong>ATTACK</strong><span>Money quiz · fast answers crit</span></button>
      <button class="mv inv" id="mInv"><strong>INVESTIGATE</strong><span>Spot the red flags · big damage</span></button>
      <button class="mv shd" id="mShd"><strong>SHIELD</strong><span>Easier question · block most of the next hit</span></button>
      <button class="mv bag" id="mBag" ${pots?"":"disabled"}><strong>BAG</strong><span>${pots?`Potions ×${pots}`:"No potions"}</span></button>
    </div>${B.kind==="wild"?`<button class="ghost" id="mRun">RUN</button>`:`<p class="small">You can't run from a boss.</p>`}`);
  on("mAtk",()=>bAsk("attack"));on("mInv",()=>bAsk("investigate"));on("mShd",()=>bAsk("shield"));on("mBag",bBag);on("mRun",bRun);
}
function bAsk(move){
  SFX.tap();B.move=move;
  const q=move==="investigate"?pickQ("inv"):pickQ(move==="shield"?"easy":"normal");
  B.q=q;B.answering=true;B.t0=performance.now();
  let lim=q.parts?40000:move==="shield"?15000:22000;
  if(!q.parts&&q.t==="deal"&&isCls("trader"))lim+=8000;
  if(B.e.spr==="sam"&&B.e.p2done)lim*=.6;
  if(B.dazed){lim*=.5;B.dazed=false}
  B.limit=lim;q.parts?renderInv(q):renderMC(q);
}
function renderMC(q){
  const label=q.t==="deal"?"MONEY MATHS":"MONEY QUIZ",mv={attack:"ATTACK",shield:"SHIELD",catch:"CATCH"}[B.move];
  const can5050=B.free5050||(S.items.scroll>0),order=shuffle(q.o.map((_,k)=>k));
  bp(`<div class="qhead"><span class="qtag ${q.t} ${q.tier===3?"t3":""}">${label}${q.tier===3?" · HARD":""}</span><span class="small">${mv}</span></div>
    <p class="q">${q.q}</p><div class="opts">${order.map(k=>`<button data-k="${k}">${q.o[k]}</button>`).join("")}</div>
    <div class="tools">${can5050?`<button id="t5050">50/50 ${B.free5050?"(FREE)":`SCROLL ×${S.items.scroll}`}</button>`:""}</div>
    <div class="timer"><i id="tfill"></i></div><div id="fb"></div>`);
  $("bpanel").querySelectorAll(".opts button").forEach(b=>b.onclick=()=>resolveMC(+b.dataset.k));
  on("t5050",()=>{if(!B.answering)return;const wrong=q.o.map((_,k)=>k).filter(k=>k!==q.a);$("bpanel").querySelector(`.opts button[data-k="${pick(wrong)}"]`).hidden=true;if(B.free5050)B.free5050=false;else S.items.scroll--;$("t5050").remove();SFX.coin()});
}
function renderInv(q){
  B.sel=new Set();const hintIdx=isCls("detective")?q.parts.findIndex(p=>p.f):-1;if(hintIdx>=0)B.sel.add(hintIdx);
  bp(`<div class="qhead"><span class="qtag inv">INVESTIGATE</span><span class="small">${q.src}</span></div>
    <p class="small">Tap every red flag in the message, then press CHECK.${hintIdx>=0?" Your detective sense revealed one.":""}</p>
    <div class="msg">${q.parts.map((p,i)=>`<button class="seg ${i===hintIdx?"hinted":""}" data-i="${i}">${p.s}</button>`).join("")}</div>
    <div class="row"><span class="small" id="flagct">${B.sel.size} flagged</span><button class="go" id="check">CHECK</button></div>
    <div class="timer"><i id="tfill"></i></div><div id="fb"></div>`);
  $("bpanel").querySelectorAll(".seg").forEach(s=>s.onclick=()=>{if(!B.answering)return;const i=+s.dataset.i;if(i===hintIdx)return;B.sel.has(i)?B.sel.delete(i):B.sel.add(i);s.classList.toggle("on");$("flagct").textContent=B.sel.size+" flagged";SFX.tap()});
  on("check",()=>resolveInv(false));
}
function pop(txt,col,x,y){fx.pops.push({txt,col,x,y,life:1})}
function play(type,dur,onHit){finishAnim();fx.anim={type,t:0,dur,onHit,hit:false}}
function finishAnim(){if(fx.anim&&!fx.anim.hit){fx.anim.hit=true;fx.anim.onHit&&fx.anim.onHit()}fx.anim=null}
function hitEnemy(d,labels){B.e.hp=Math.max(0,B.e.hp-d);fx.shake=8;fx.flash=1;fx.kb=10;SFX.hit();pop("-"+d,"#fff",180,60);labels.forEach((l,i)=>pop(l,"#ffc94a",180,46-i*12));for(let i=0;i<10;i++)fx.parts.push({x:176,y:120,vx:(Math.random()-.3)*3,vy:-Math.random()*3,life:1,col:"#ffc94a"})}
function weakCheck(){if(B.e.weak&&B.move===B.e.weak){const first=!S.notes[B.e.n];S.notes[B.e.n]=B.e.weak;return{m:1.5,first}}return{m:1,first:false}}
function feedbackRow(q,msg,extra=""){
  $("fb").innerHTML=`<p class="btext" style="font-size:17px">${msg}</p>${extra}<p class="explain">${q.e}</p>
    <div class="row"><a class="learn" href="${guideURL(q.learn)}" target="_blank" rel="noopener">Want to learn more? ↗</a><button class="go" id="bnext">CONTINUE</button></div>`;
  $("bnext").focus();on("bnext",()=>{SFX.tap();afterPlayer()});
}
function resolveMC(k){
  if(!B||!B.answering)return;B.answering=false;
  const q=B.q,ok=k===q.a,el=performance.now()-B.t0;
  $("bpanel").querySelectorAll(".opts button").forEach(b=>{const j=+b.dataset.k;b.disabled=true;if(j===q.a)b.classList.add("right");else if(j===k)b.classList.add("wrong")});
  if($("t5050"))$("t5050").remove();
  let msg="";
  if(B.move==="catch"){
    if(ok){const card=B.e.card,dup=!!S.cards[card];S.cards[card]=1;B.caught=true;fx.flash=1;SFX.win();msg=dup?`<b class="ok">Caught!</b> You already had this card, so it turned into +${gainCoins(10)} coins.`:`<b class="ok">Gotcha! ${B.e.n} card added.</b> Power it up from MENU → CARDS.`;emit("catch")}
    else{SFX.hurt();B.escaped=true;msg=`<b class="bad">It slipped back into the grass!</b>`}
  }else if(B.move==="shield"){
    if(ok){B.shield=true;S.hp=Math.min(maxHP(),S.hp+3);SFX.coin();play("shield",600);msg=`<b class="ok">Shield up!</b> The next hit will be mostly blocked. +3 HP.`}
    else{B.counter=true;B.streak=0;SFX.hurt();msg=`<b class="bad">Your shield failed!</b> The enemy is ready to counter.`}
  }else{
    if(ok){const fast=el<6000,mult=1+.25*Math.min(B.streak,4),w=weakCheck(),d=Math.round(atk()*mult*(fast?1.5:1)*w.m);B.streak++;
      const labels=[];if(fast)labels.push("CRIT!");if(w.m>1)labels.push("WEAK SPOT!");
      SFX.whoosh();play("attack",650,()=>hitEnemy(d,labels));
      msg=`<b class="ok">${fast?"Critical hit!":"Hit!"} −${d} HP</b>${w.m>1?` <span class="hint">WEAK SPOT!${w.first?" Penny noted it.":""}</span>`:""}${mult>1?` <span class="hint">streak ×${mult.toFixed(2)}</span>`:""}`}
    else{B.streak=0;B.counter=true;SFX.hurt();msg=`<b class="bad">${k<0?"Time's up!":"Missed!"}</b> The enemy will counter-attack harder.`}
  }
  hud();feedbackRow(q,msg);
}
function resolveInv(timeout){
  if(!B||!B.answering)return;B.answering=false;
  const q=B.q,flags=q.parts.map((p,i)=>p.f?i:-1).filter(i=>i>=0),found=flags.filter(i=>B.sel.has(i)).length,wrong=[...B.sel].filter(i=>!q.parts[i].f).length;
  const ratio=timeout?0:Math.max(0,(found-.5*wrong)/flags.length);
  $("bpanel").querySelectorAll(".seg").forEach(s=>{const i=+s.dataset.i,p=q.parts[i];s.disabled=true;s.classList.remove("on","hinted");if(p.f)s.classList.add(B.sel.has(i)?"found":"missed");else if(B.sel.has(i))s.classList.add("wrongtap")});
  $("check").disabled=true;
  let msg;
  if(ratio>=.5){const w=weakCheck(),mult=(1+.15*Math.min(B.streak,4))*(isCls("detective")?1.2:1)*w.m,d=Math.round(atk()*2*ratio*mult);B.streak++;
    const labels=[];if(ratio===1)labels.push("PERFECT!");if(w.m>1)labels.push("WEAK SPOT!");
    SFX.beam();play("beam",900,()=>hitEnemy(d,labels));
    msg=`<b class="ok">${ratio===1?"PERFECT investigation!":"Good detective work!"} −${d} HP</b> (${found}/${flags.length} flags${wrong?`, ${wrong} wrong tap${wrong>1?"s":""}`:""})${w.m>1?` <span class="hint">WEAK SPOT!${w.first?" Penny noted it.":""}</span>`:""}`}
  else{B.streak=0;B.counter=true;SFX.hurt();msg=`<b class="bad">${timeout?"Time's up!":"Not enough evidence!"}</b> ${found}/${flags.length} flags found${wrong?`, ${wrong} wrong tap${wrong>1?"s":""}`:""}. The enemy will counter.`}
  hud();feedbackRow(q,msg,`<ul class="flags">${flags.map(i=>`<li>${B.sel.has(i)?"✔":"✘"} <b>${q.parts[i].s.trim()}</b> ${q.parts[i].w}</li>`).join("")}</ul>`);
}
function afterPlayer(){
  finishAnim();const e=B.e;
  if(B.kind==="offer"){bEnd();return}
  if(e.hp<=0){bVictory();return}
  if(B.kind==="boss"&&!e.p2done&&e.hp<=e.max/2){e.p2done=true;e.atk+=3;e.tier=3;fx.shake=14;fx.banner=1200;SFX.alert();
    bp(`<p class="btext" style="color:var(--bad)">⚠ ${e.p2}</p><button class="go wide" id="bgo">CONTINUE</button>`);on("bgo",bEnemy);$("bgo").focus();return}
  bEnemy();
}
function bEnemy(){
  finishAnim();const e=B.e;const special=!B.shield&&Math.random()<.22;const mv=special?"Dizzy Spin":pick(e.moves);
  let d=Math.round(e.atk*(.85+Math.random()*.3)*(B.counter?1.5:1)*(special?.6:1));
  const shielded=B.shield;if(shielded)d=Math.max(1,Math.round(d*.25));
  const wasCounter=B.counter;B.shield=false;B.counter=false;if(special)B.dazed=true;
  play("enemy",650,()=>{S.hp=Math.max(0,S.hp-d);fx.phit=1;fx.pkb=10;SFX.hurt();pop("-"+d,"#ff6470",60,92);hud()});
  const ko=S.hp-d<=0;
  bp(`<p class="btext">${e.n} used <strong>${mv.toUpperCase()}</strong>! ${shielded?"Your shield took most of it. ":""}${wasCounter&&!shielded?"It's a counter-attack! ":""}<b class="bad">−${d} HP</b>${special?" <span class=\"bad\">You're DAZED: your next question has half the time.</span>":""}</p>
    <button class="go wide" id="bgo">${ko?"...":"CONTINUE"}</button>`);
  on("bgo",()=>{SFX.tap();finishAnim();S.hp<=0?bBlackout():bMenu()});$("bgo").focus();
}
function bBag(){
  const rows=["potion","superpotion"].filter(k=>S.items[k]>0).map(k=>`<button class="mv bag" data-it="${k}"><strong>${ITEMS[k].n.toUpperCase()} ×${S.items[k]}</strong><span>${ITEMS[k].d} Uses your turn.</span></button>`).join("");
  bp(`<p class="btext">Use which item?</p><div class="moves">${rows}</div><button class="ghost" id="bback">BACK</button>`);
  $("bpanel").querySelectorAll("[data-it]").forEach(b=>b.onclick=()=>{const k=b.dataset.it;S.items[k]--;const h=Math.min(maxHP()-S.hp,ITEMS[k].heal);S.hp+=h;SFX.coin();hud();play("shield",500);
    bp(`<p class="btext">You used a ${ITEMS[k].n}. <b class="ok">+${h} HP</b></p><button class="go wide" id="bgo">CONTINUE</button>`);on("bgo",bEnemy);$("bgo").focus()});
  on("bback",bMenu);
}
function bRun(){
  if(B.kind==="offer"||isCls("scout")||Math.random()<.75){bp(`<p class="btext">${B.kind==="offer"?"You let it go.":"Got away safely!"}</p><button class="go wide" id="bgo">CONTINUE</button>`);on("bgo",bEnd);$("bgo").focus();return}
  bp(`<p class="btext">Couldn't get away!</p><button class="go wide" id="bgo">CONTINUE</button>`);on("bgo",bEnemy);$("bgo").focus();
}
function bVictory(){
  const e=B.e;fx.dead=.99;SFX.win();
  const xp=gainXP(e.xp),coins=gainCoins(e.coins);let extra="";
  if(B.kind==="boss"){
    const first=!S.freed[e.id];S.freed[e.id]=true;const cards=[];
    [e.cards[0]].concat(S.hp>=maxHP()/2?[e.cards[1]]:[]).forEach(cid=>{const n=!S.cards[cid];S.cards[cid]=1;cards.push({cid,n})});
    emit("boss:"+e.id);
    extra=`<p class="btext">${e.n}: “${e.lose}”</p>${first?`<p class="small">The ${e.id==="bank"?"Bank":"Market"} is free!</p>`:""}
      <div class="drops">${cards.map((d,i)=>cardHTML(d.cid,true,d.n,i)).join("")}</div>
      ${S.hp<maxHP()/2?`<p class="small">Finish a boss with more than half your HP to drop its Legendary card.</p>`:""}
      <a class="learn" href="${guideURL(e.guide)}" target="_blank" rel="noopener">Read the ${e.gname} on Money Hunters ↗</a>`;
  }else emit("goblin");
  bp(`<p class="btext"><b class="ok">VICTORY!</b> ${e.n} was defeated.</p><p class="small">+${xp} XP · +${coins} coins</p>${extra}<button class="go wide" id="bgo">BACK TO MAP</button>`);
  on("bgo",bEnd);$("bgo").focus();
}
function bBlackout(){
  SFX.hurt();B=null;heal();MAP=MAPS.town;P.x=P.fx=5;P.y=P.fy=29;P.dir=2;P.moving=false;
  mode="world";$("bpanel").hidden=true;$("controls").hidden=false;lastZone="";hud();
  say([{s:"PENNY",t:"Ouch! The Scam Gang got you that time. I carried you home and patched you up."},{s:"PENNY",t:"Use SHIELD when you're low, and hit their weak spots. You'll get them next time!"}]);
}
function bEnd(){B=null;mode="world";$("bpanel").hidden=true;$("controls").hidden=false;sinceBattle=0;hud();save()}

function wallet(x,name,lv,hp,max,disp,right){
  R(x,6,112,30,"rgba(10,12,30,.82)");R(x,6,112,2,"#ffc94a");
  txt(name.slice(0,17),right?x+106:x+6,name.length>12?12:11,name.length>12?4:6,"#f3f0ff",right?"right":"left");
  if(max){txt("Lv"+lv,right?x+6:x+106,11,6,"#ffc94a",right?"left":"right");
    R(x+6,23,100,7,"#2a2e4a");const pr=Math.max(0,disp/max);const w=Math.round(98*pr);R(right?x+7+98-w:x+7,24,w,5,pr>.5?"#4cc27a":pr>.2?"#e8b83a":"#e84a5a");
    R(right?x+6:x+92,22,9,9,"#ffc94a");R(right?x+8:x+94,24,5,5,"#b8861a")}
  else txt("WILD OFFER",right?x+106:x+6,23,6,"#ffc94a",right?"right":"left");
}
function drawBattle(t,dt){
  const e=B.e,boss=B.kind==="boss";
  if(fx.anim){const a=fx.anim;a.t+=dt;if(!a.hit&&a.t>=a.dur*.6){a.hit=true;a.onHit&&a.onHit()}if(a.t>=a.dur)fx.anim=null}
  const a=fx.anim,p=a?a.t/a.dur:0;
  if(boss){R(0,0,240,208,e.bg[0]);for(let x=8;x<240;x+=40)R(x,44,22,60,"rgba(255,255,255,.06)");R(0,150,240,58,e.bg[1]);R(0,150,240,2,"rgba(255,255,255,.15)")}
  else{R(0,0,240,110,"#bfe6f5");R(0,80,240,30,"#8fd08a");for(let x=-10;x<250;x+=30){c.fillStyle="#5aa860";c.beginPath();c.arc(x,96,18,Math.PI,0);c.fill()}R(0,110,240,98,"#9ad07a");R(0,150,240,58,"#86c06a");for(let x=0;x<240;x+=12)R(x+(x%24?3:0),156+(x%3)*8,2,3,"#6aa858")}
  // positions
  let px=44,ex=180;
  if(a&&a.type==="attack")px+=Math.round(60*Math.sin(Math.PI*Math.min(1,p)));
  if(a&&a.type==="enemy")ex-=Math.round(70*Math.sin(Math.PI*Math.min(1,p)));
  if(fx.kb>.5){ex+=Math.round(fx.kb);fx.kb*=.85}else fx.kb=0;
  if(fx.pkb>.5){px-=Math.round(fx.pkb);fx.pkb*=.85}else fx.pkb=0;
  if(fx.shake>.5){ex+=Math.round((Math.random()-.5)*fx.shake);fx.shake*=.86}else fx.shake=0;
  c.fillStyle="rgba(0,0,0,.2)";c.beginPath();c.ellipse(ex,174,30,6,0,0,7);c.fill();c.beginPath();c.ellipse(px+24,174,22,5,0,0,7);c.fill();
  // enemy
  const intro=Math.min(1,(fx.intro=(fx.intro||0)+dt/400));const slide=Math.round((1-intro)*120);
  if(!(e.hp<=0&&fx.dead<.03)&&!(B.caught&&fx.dead<.03)){
    c.save();c.translate(ex+slide,e.spr==="goblin"?158:e.spr==="offer"?132:150);
    if((B.kind!=="offer"&&e.hp<=0)||B.caught){fx.dead*=.93;c.globalAlpha=Math.max(0,fx.dead);c.translate(0,(1-fx.dead)*12)}
    if(fx.flash>.05){c.filter="brightness(3)";fx.flash*=.75}
    SPR[e.spr](c,t,e);c.restore();c.filter="none";c.globalAlpha=1;
  }
  // player (side view)
  c.save();c.translate(px-slide,124);c.scale(3,3);drawPlayer(c,0,0,1,a&&a.type==="attack"?Math.floor(p*6)%2:0);c.restore();
  // move effects
  if(a&&a.type==="attack"&&p>.15&&p<.62){const k=(p-.15)/.47;for(let i=0;i<3;i++){const cx=Math.round(px+40+(ex-px-40)*Math.min(1,k+i*.08)),cy=Math.round(138-Math.sin(Math.PI*Math.min(1,k+i*.08))*26);R(cx,cy,6,6,"#ffc94a");R(cx+2,cy+1,2,4,"#b8861a")}}
  if(a&&a.type==="beam"&&p>.1&&p<.85){c.globalAlpha=.35+.25*Math.sin(t/40);c.fillStyle="#ffe36a";c.beginPath();c.moveTo(px+42,134);c.lineTo(ex-6,112);c.lineTo(ex-6,150);c.closePath();c.fill();c.globalAlpha=1;
    c.strokeStyle="#ffc94a";c.lineWidth=3;c.beginPath();c.arc(px+44,134,7,0,7);c.stroke();R(px+48,139,6,3,"#8a5a2a")}
  if((a&&a.type==="shield")||B.shield){const rr=a&&a.type==="shield"?22+8*p:28;c.globalAlpha=.35+.15*Math.sin(t/150);c.strokeStyle="#4ad0ff";c.lineWidth=3;c.beginPath();c.arc(px+24,148,rr,0,7);c.stroke();c.fillStyle="rgba(74,208,255,.12)";c.fill();c.globalAlpha=1}
  if(fx.phit>.03){R(0,0,240,208,`rgba(255,60,80,${fx.phit*.4})`);fx.phit*=.88}
  fx.parts=fx.parts.filter(q=>{q.x+=q.vx;q.y+=q.vy;q.vy+=.12;q.life-=.025;R(Math.round(q.x),Math.round(q.y),3,3,q.col);return q.life>0});
  // wallets
  fx.pDisp+=(S.hp-fx.pDisp)*.15;fx.eDisp+=((e.hp||0)-fx.eDisp)*.15;
  wallet(4,S.name,S.lvl,S.hp,maxHP(),fx.pDisp,false);
  wallet(124,e.n.toUpperCase(),e.lv,e.hp,e.max,fx.eDisp,true);
  txt(`${S.hp}/${maxHP()}`,11,41,6,"#000");txt(`${S.hp}/${maxHP()}`,10,40,6,"#f3f0ff");
  if(B.dazed){R(4,48,40,10,"#ff6470");txt("DAZED",24,50,5,"#fff","center")}
  fx.pops=fx.pops.filter(q=>{q.y-=.5;q.life-=.02;c.globalAlpha=Math.max(0,q.life);txt(q.txt,q.x+1,q.y+1,8,"#000","center");txt(q.txt,q.x,q.y,8,q.col,"center");c.globalAlpha=1;return q.life>0});
  if(fx.banner>0){fx.banner-=dt;const k=Math.min(1,fx.banner/300);R(0,0,240,30*k,"#000");R(0,208-30*k,240,30*k,"#000");if(fx.banner>200){R(0,92,240,26,"rgba(184,40,60,.9)");txt(e.p2done?"PHASE 2":"BOSS BATTLE",120,96,6,"#ffc94a","center");txt(e.n.toUpperCase(),120,106,8,"#fff","center")}}
  if(B.answering){const rem=B.limit-(performance.now()-B.t0),tf=$("tfill");if(tf){tf.style.width=Math.max(0,rem/B.limit*100)+"%";tf.classList.toggle("low",rem<6000)}if(rem<=0){B.q.parts?resolveInv(true):resolveMC(-1)}}
}
