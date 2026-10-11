// main.js: sound, UI helpers, menus, title/creator, input and boot.
let AC=null;
function beep(f,d=.08,type="square",v=.035){if(S.muted)return;try{AC=AC||new(window.AudioContext||window.webkitAudioContext)();const o=AC.createOscillator(),g=AC.createGain();o.type=type;o.frequency.value=f;g.gain.value=v;o.connect(g);g.connect(AC.destination);o.start();g.gain.exponentialRampToValueAtTime(.0001,AC.currentTime+d);o.stop(AC.currentTime+d+.02)}catch(e){}}
const SFX={hit(){beep(660,.06);setTimeout(()=>beep(990,.08),60)},hurt(){beep(150,.25,"sawtooth",.05)},win(){[523,659,784,1046].forEach((f,i)=>setTimeout(()=>beep(f,.14),i*110))},coin(){beep(1250,.05)},tap(){beep(520,.03,"triangle",.03)},bump(){beep(110,.05,"triangle",.04)},lvl(){[784,988,1318].forEach((f,i)=>setTimeout(()=>beep(f,.1),i*90))},grass(){beep(300+rnd(80),.03,"triangle",.015)},alert(){[880,660,880].forEach((f,i)=>setTimeout(()=>beep(f,.07),i*80))},whoosh(){beep(240,.12,"triangle",.03)},beam(){beep(1400,.2,"sine",.025)}};
let toastT,bannerT;
function toast(msg){const t=$("toast");t.textContent=msg;t.hidden=false;t.style.animation="none";t.offsetHeight;t.style.animation="";clearTimeout(toastT);toastT=setTimeout(()=>t.hidden=true,2600)}
function modal(html){$("box").innerHTML=html;$("ov").hidden=false;$("box").scrollTop=0}
function closeModal(){$("ov").hidden=true}
function banner(txt){const b=$("banner");b.textContent=txt;b.hidden=false;b.style.animation="none";b.offsetHeight;b.style.animation="";clearTimeout(bannerT);bannerT=setTimeout(()=>b.hidden=true,1800)}
function hud(){
  if(!S.cls)return;
  $("tWho").textContent=`LV ${S.lvl} ${S.name}`;
  const r=S.hp/maxHP();$("tHp").style.width=Math.max(0,r*100)+"%";$("tHp").style.background=r>.5?"var(--good)":r>.2?"var(--coin)":"var(--bad)";
  $("tXp").style.width=(S.xp/xpNeed(S.lvl)*100)+"%";$("tCoins").textContent=S.coins;$("mute").style.opacity=S.muted?.4:1;
}
const bp=html=>{$("bpanel").innerHTML=html};
function on(id,fn){const e=$(id);if(e)e.onclick=fn}
let DQ=null;
function say(lines,done){DQ={lines:lines.map(l=>typeof l==="string"?{s:"",t:l}:l),i:0,done,shown:0,full:false};$("dialog").hidden=false;showLine()}
function showLine(){const l=DQ.lines[DQ.i];$("spk").textContent=l.s||"";$("spk").hidden=!l.s;DQ.shown=0;DQ.full=false;$("choices").innerHTML="";$("more").hidden=true;$("dtext").textContent=""}
function finishLine(){
  const l=DQ.lines[DQ.i];DQ.full=true;$("dtext").textContent=l.t;
  if(l.choices){$("choices").innerHTML=l.choices.map((c,i)=>`<button data-c="${i}">${c.label}</button>`).join("");
    $("choices").querySelectorAll("button").forEach(b=>b.onclick=e=>{e.stopPropagation();const c=l.choices[+b.dataset.c];DQ=null;$("dialog").hidden=true;SFX.tap();c.fn&&c.fn()});$("choices").querySelector("button").focus()}
  else $("more").hidden=false;
}
function advance(){if(!DQ)return;if(!DQ.full){finishLine();return}if(DQ.lines[DQ.i].choices)return;SFX.tap();DQ.i++;if(DQ.i>=DQ.lines.length){const d=DQ.done;DQ=null;$("dialog").hidden=true;d&&d()}else showLine()}
$("dialog").addEventListener("click",advance);
function cardHTML(cid,owned,isNew=false,i=0){
  const k=CARDS[cid],rar={C:"COMMON",R:"RARE",L:"LEGENDARY"}[k.r],pw=S.powered[cid];
  if(!owned)return`<div class="card locked r${k.r}"><span class="rar">${rar}</span><span class="ico">?</span><span class="cn">???</span></div>`;
  return`<button class="card r${k.r} ${pw?"pow":""} ${isNew?"new":""}" data-c="${cid}" style="animation-delay:${i*.3}s"><span class="rar">${pw?"POWERED":rar}</span><span class="ico">${k.icon}</span><span class="cn">${k.n}</span></button>`;
}
function openBoard(){
  const d=daily();d.read=true;save();const g=gemSpot(),side=g[0]<19?"west":"east",half=g[1]<18?"north":"south",all=d.gem&&d.gob>=3&&d.mystery;
  const tick=v=>v?`<span class="st">DONE</span>`:`<span class="st" style="color:var(--muted)">TO DO</span>`;
  modal(`<h2>COINSWORTH NOTICEBOARD</h2><p class="small">Daily Hunt for ${d.date}. New tasks every day. Miss a day? Nothing is lost.</p>
    <div class="list">
      <div class="li ${d.gem?"done":""}"><div><h3>FIND TODAY'S GEM</h3><p>A gem is sparkling in Route 1, on the ${side} side, towards the ${half}.</p></div>${tick(d.gem)}</div>
      <div class="li ${d.gob>=3?"done":""}"><div><h3>BEAT 3 GOBLINS</h3><p>${d.gob}/3 defeated today.</p></div>${tick(d.gob>=3)}</div>
      <div class="li ${d.mystery?"done":""}"><div><h3>DAILY MYSTERY</h3><p>Investigate today's suspicious message.</p></div>${d.mystery?tick(true):`<button class="go" id="mys">SOLVE</button>`}</div>
    </div>
    ${d.claimed?`<p class="small ok">Today's reward claimed. Days played this month: ${S.played?S.played.n:0}. See you tomorrow!</p>`:`<button class="go wide" id="claim" ${all?"":"disabled"}>CLAIM REWARD · 50 COINS + 40 XP</button>`}
    <div class="li"><div><h3>NOTICE</h3><p>Coinsworth Bank now runs a free switch simulator. Ask Clara at the counter.</p></div></div>
    <button class="ghost" id="cl">CLOSE</button>`);
  on("cl",closeModal);on("mys",dailyMystery);
  on("claim",()=>{if(!all)return;d.claimed=true;/* days counted in daily() */toast("DAILY HUNT COMPLETE · "+reward({coins:50,xp:40}));SFX.win();hud();save();openBoard()});
}
function dailyMystery(){
  const q=INV[hashStr("m"+today())%INV.length];const sel=new Set();
  modal(`<h2>DAILY MYSTERY</h2><p class="small">${q.src}. Tap every red flag, then CHECK. Get at least 3 in 4 right to solve it.</p>
    <div class="msg">${q.parts.map((p,i)=>`<button class="seg" data-i="${i}">${p.s}</button>`).join("")}</div>
    <div class="row"><button class="ghost" id="bk">BACK</button><button class="go" id="ck">CHECK</button></div><div id="mfb"></div>`);
  $("box").querySelectorAll(".seg").forEach(s=>s.onclick=()=>{const i=+s.dataset.i;sel.has(i)?sel.delete(i):sel.add(i);s.classList.toggle("on")});
  on("bk",openBoard);
  on("ck",()=>{const flags=q.parts.map((p,i)=>p.f?i:-1).filter(i=>i>=0),found=flags.filter(i=>sel.has(i)).length,wrong=[...sel].filter(i=>!q.parts[i].f).length,ratio=Math.max(0,(found-.5*wrong)/flags.length);
    $("box").querySelectorAll(".seg").forEach(s=>{const i=+s.dataset.i,p=q.parts[i];s.disabled=true;s.classList.remove("on");if(p.f)s.classList.add(sel.has(i)?"found":"missed");else if(sel.has(i))s.classList.add("wrongtap")});
    const solved=ratio>=.75;if(solved){daily().mystery=true;save();SFX.win()}else SFX.hurt();
    $("mfb").innerHTML=`<p class="btext" style="font-size:17px">${solved?'<b class="ok">Mystery solved!</b>':'<b class="bad">Not quite.</b> Study the flags and try again tomorrow.'}</p><ul class="flags">${flags.map(i=>`<li>${sel.has(i)?"✔":"✘"} <b>${q.parts[i].s.trim()}</b> ${q.parts[i].w}</li>`).join("")}</ul><p class="explain">${q.e}</p><a class="learn" href="${guideURL(q.learn)}" target="_blank" rel="noopener">Want to learn more? ↗</a>`;
    $("ck").outerHTML=`<button class="go" id="done">BACK TO BOARD</button>`;on("done",openBoard)});
}
function weeklyDrop(){
  if(S.age===false){say([{s:"DEE",t:"Here's this week's money tip: "+TIPS[weekNo()%TIPS.length]}]);return}
  if(S.age===null){say([{s:"DEE",t:"Guides are open to everyone, and live offers are adults only. Are you 18 or over?",choices:[{label:"YES, 18+",fn:()=>{S.age=true;save();weeklyDrop()}},{label:"NO",fn:()=>{S.age=false;save();weeklyDrop()}}]}]);return}
  const cat=WEEKLY[weekNo()%WEEKLY.length];
  modal(`<h2>DEE'S WEEKLY DROP</h2>
    <div class="li"><div><h3>THIS WEEK: ${cat.toUpperCase()}</h3><p>Dee: “Lots of hunters are asking about ${cat.toLowerCase()}. The full guide is on Money Hunters, with any live offers clearly labelled.”</p></div></div>
    <div class="li"><div><h3>TIP OF THE WEEK</h3><p>${TIPS[weekNo()%TIPS.length]}</p></div></div>
    <a class="cta" href="${guideURL(WEEKLY_GUIDES[cat]||"pb-budget-basics")}" target="_blank" rel="noopener">READ THE ${cat.toUpperCase()} GUIDE ↗</a>
    <p class="small">Some links on Money Hunters pay us. They never affect the game, and the game never rewards you for signing up to anything.</p>
    <button class="ghost" id="cl">CLOSE</button>`);on("cl",closeModal);
}
const price=p=>isCls("trader")?Math.round(p*.8):p;
function openShop(){
  modal(`<h2>HUNTER MART</h2><p class="small">Coins come from playing and learning. You have <b style="color:var(--coin)">${S.coins}</b>.${isCls("trader")?" Trader discount applied.":""}</p>
    <div class="list">${Object.entries(ITEMS).map(([k,it])=>`<div class="li"><div><h3>${it.n.toUpperCase()}</h3><p>${it.d} You have ${S.items[k]||0}.</p></div><button class="go" data-b="${k}" ${S.coins<price(it.p)?"disabled":""}>◉ ${price(it.p)}</button></div>`).join("")}</div>
    <button class="ghost" id="cl">CLOSE</button>`);
  $("box").querySelectorAll("[data-b]").forEach(b=>b.onclick=()=>{const k=b.dataset.b,p=price(ITEMS[k].p);if(S.coins<p)return;S.coins-=p;S.items[k]=(S.items[k]||0)+1;SFX.coin();hud();save();openShop()});
  on("cl",closeModal);
}
let menuTab="missions";
function openMenu(tab){
  if(tab)menuTab=tab;
  const tabs=["missions","cards","bag","hunter"].map(t=>`<button class="${t===menuTab?"on":""}" data-t="${t}">${t.toUpperCase()}</button>`).join("");let body="";
  if(menuTab==="missions"){const row=m=>{const st=mS(m.id),lock=!st.on&&!st.done;return`<div class="li ${st.done?"done":""} ${lock?"lock":""}"><div><h3>${lock&&!m.side?"???":m.title.toUpperCase()}</h3><p>${lock&&!m.side?"Complete earlier missions to unlock.":m.desc}</p></div><span class="st">${st.done?"DONE":lock?"":`${st.p}/${m.need}`}</span></div>`};
    const side=MISSIONS.filter(m=>m.side&&(mS(m.id).on||mS(m.id).done));body=`<div class="list">${MISSIONS.filter(m=>!m.side).map(row).join("")}</div>${side.length?`<h2>SIDE QUESTS</h2><div class="list">${side.map(row).join("")}</div>`:""}`}
  if(menuTab==="cards")body=`<p class="small">${Object.keys(S.cards).length}/${Object.keys(CARDS).length} collected. Wild Offer cards can be powered up on Money Hunters.</p><div class="grid">${Object.keys(CARDS).map(cid=>cardHTML(cid,!!S.cards[cid])).join("")}</div>`;
  if(menuTab==="bag")body=`<div class="list">${Object.entries(ITEMS).map(([k,it])=>`<div class="li"><div><h3>${it.n.toUpperCase()} ×${S.items[k]||0}</h3><p>${it.d}</p></div>${it.heal&&S.items[k]>0&&S.hp<maxHP()?`<button class="go" data-u="${k}">USE</button>`:""}</div>`).join("")}</div>`;
  if(menuTab==="hunter"){const k=CLASSES[S.cls],notes=Object.entries(S.notes);
    body=`<div class="li"><div><h3>${S.name} · ${k.n}</h3><p>${k.skill}: ${k.d}</p></div></div>
      <div class="li"><div><h3>LEVEL ${S.lvl}</h3><p>HP ${S.hp}/${maxHP()} · Attack ${atk()} · XP ${S.xp}/${xpNeed(S.lvl)} · Coins ${S.coins}</p></div></div>
      <div class="li"><div><h3>PENNY'S WEAK-SPOT NOTES</h3><p>${notes.length?notes.map(([n,w])=>`${n}: ${w}`).join(" · "):"None yet. Hit an enemy's weak spot to record it."}</p></div></div>
      <div class="li"><div><h3>PROGRESS</h3><p>Bosses ${Object.keys(S.freed).length}/2 · Cards ${Object.keys(S.cards).length}/${Object.keys(CARDS).length} · Questions seen ${S.seen.length}/${QS.length} · Days played this month ${S.played?S.played.n:0}</p></div></div>
      <p class="small">Your game saves automatically in this browser. Change your look at Home.</p><button class="ghost" id="reset">START OVER</button><div id="rs"></div>`}
  modal(`<div class="tabs">${tabs}</div>${body}<button class="ghost" id="cl">CLOSE</button>`);
  $("box").querySelectorAll("[data-t]").forEach(b=>b.onclick=()=>openMenu(b.dataset.t));
  $("box").querySelectorAll(".card[data-c]").forEach(b=>b.onclick=()=>showCard(b.dataset.c));
  $("box").querySelectorAll("[data-u]").forEach(b=>b.onclick=()=>{const k=b.dataset.u;S.items[k]--;S.hp=Math.min(maxHP(),S.hp+ITEMS[k].heal);SFX.coin();hud();save();openMenu()});
  on("reset",()=>{$("rs").innerHTML=`<p class="small">This erases your hunter. Are you sure?</p><div class="row"><button class="go" id="ry" style="background:var(--bad);box-shadow:none">ERASE</button><button class="ghost" id="rn">KEEP</button></div>`;on("rn",()=>$("rs").innerHTML="");on("ry",()=>{try{localStorage.removeItem("mh_coinsworth")}catch(e){}S=DEF();MAP=MAPS.town;closeModal();toTitle()})});
  on("cl",closeModal);
}
function showCard(cid){
  const k=CARDS[cid],pw=S.powered[cid];
  modal(`<div class="drops">${cardHTML(cid,true)}</div><h2>${k.n.toUpperCase()}</h2><p class="q" style="font-size:17px">${k.t}</p>${pw?`<p class="small" style="color:var(--coin)">Powered: ${k.pt}</p>`:""}
    ${k.type==="offer"&&!pw?`<div class="li"><div><h3>POWER UP THIS CARD</h3><p>A code word is hidden in the ${k.gname} on Money Hunters. Find it to power up this card (+30 XP).</p></div></div>
      <a class="cta" href="${guideURL(k.guide)}" target="_blank" rel="noopener">OPEN THE ${k.gname.toUpperCase()} ↗</a>
      <div class="coderow"><input id="code" maxlength="12" autocomplete="off" spellcheck="false" aria-label="Code word"><button class="go" id="sub">CHECK</button></div><p class="err" id="err" aria-live="polite"></p>
      <p class="demo">Demo build: the code word is <b>HUNT</b>. In the real game each guide hides its own word.</p>`:""}
    <button class="ghost" id="bk">BACK</button>`);
  on("bk",()=>openMenu("cards"));
  const check=()=>{if($("code").value.trim().toUpperCase()==="HUNT"){S.powered[cid]=true;toast(`CARD POWERED UP · +${gainXP(30)} XP`);SFX.win();hud();save();showCard(cid)}else{$("err").textContent="That's not the word. Look near the bottom of the guide.";SFX.hurt()}};
  on("sub",check);if($("code"))$("code").addEventListener("keydown",e=>{if(e.key==="Enter")check()});
}
const stars=[...Array(40)].map(()=>[rnd(240),rnd(120),Math.random()*6]);
function drawTitle(t){
  R(0,0,240,208,"#10132b");stars.forEach(([x,y,p])=>{if(Math.sin(t/400+p)>-.3)R(x,y,1,1,"#cfd3ff")});R(0,150,240,58,"#1b2048");
  [[8,118,30,32],[44,104,24,46],[74,124,36,26],[118,96,28,54],[152,116,34,34],[192,108,40,42]].forEach(([x,y,w,h],i)=>{R(x,y,w,h,"#232a5c");for(let k=0;k<3;k++)if((i+k+Math.floor(t/900))%3)R(x+5+k*8,y+8,4,4,"#ffc94a")});
  txt("MONEY HUNTERS",120,22,8,"#ffc94a","center");txt("COINSWORTH",122,42,16,"#b8283c","center");txt("COINSWORTH",120,40,16,"#f3f0ff","center");txt("a money adventure",120,66,6,"#a7aad4","center");
  [["ogre",60],["goblin",120],["sam",180]].forEach(([s,x],i)=>{c.save();c.translate(x,176+Math.round(Math.sin(t/300+i)*2));c.scale(.7,.7);SPR[s](c,t,GOBLINS[0]);c.restore()});
}
let introPenny=false;
function drawIntro(t){R(0,0,240,208,"#0c0f22");stars.forEach(([x,y,p])=>{if(Math.sin(t/500+p)>0)R(x,y+40,1,1,"#8a8fc0")});if(introPenny){c.save();c.translate(88,40);c.scale(4,4);drawPerson(c,0,0,2,MAPS.town.npcs[0].look,0);c.restore()}}
function toTitle(){
  mode="title";$("topbar").hidden=true;$("controls").hidden=true;$("bpanel").hidden=false;$("dialog").hidden=true;DQ=null;
  bp(`<div class="titlebtns">${S.started?`<button class="big" id="cont">CONTINUE</button>`:""}<button class="${S.started?"ghost":"big"}" id="newg">NEW GAME</button></div>
    <p class="small">Explore Coinsworth, beat the Scam Gang, catch Wild Offers and learn real money skills. Demo build: progress saves in this browser.</p>`);
  on("cont",()=>{SFX.tap();enterWorld(false)});
  on("newg",()=>{SFX.tap();if(S.started){bp(`<p class="btext">Start a new game? Your current hunter will be erased.</p><div class="row"><button class="go" id="y">START OVER</button><button class="ghost" id="n">BACK</button></div>`);on("n",toTitle);on("y",()=>{S=DEF();MAP=MAPS.town;startIntro()})}else startIntro()});
}
function startIntro(){
  mode="intro";$("bpanel").hidden=true;introPenny=false;
  say(["Welcome to Coinsworth: a quiet little town where people work hard for their money.","Then the SCAM GANG moved in.","Hidden fees. Fake deals. Too-good-to-be-true texts. Bit by bit, they drained everyone's savings.","The Overdraft Ogre seized the Bank's vault. Shrinkflation Sam took the Market. And their boss, the Scam King, is planning something big..."],
  ()=>{introPenny=true;say([{s:"PENNY",t:"Oh! Hello there. I'm Penny. I've been hunting deals in this town for thirty years."},{s:"PENNY",t:"Coinsworth needs a new Money Hunter: someone who can spot a scam, find real value and help others do the same."},{s:"PENNY",t:"Every hunter has a special talent. Which one is yours?"}],chooseClass)});
}
function chooseClass(){
  let sel=null;
  modal(`<h2>CHOOSE YOUR TALENT</h2><div class="classes">${Object.entries(CLASSES).map(([k,v])=>`<button class="cls" data-k="${k}"><strong>${v.n}</strong><em>${v.skill}</em></button>`).join("")}</div>
    <p class="clsinfo" id="ci">Tap a talent to see what it does.</p><button class="go wide" id="pick" disabled>CHOOSE</button>`);
  $("box").querySelectorAll(".cls").forEach(b=>b.onclick=()=>{sel=b.dataset.k;$("box").querySelectorAll(".cls").forEach(x=>x.classList.toggle("on",x===b));$("ci").textContent=CLASSES[sel].d;$("pick").disabled=false;$("pick").textContent="BE A "+CLASSES[sel].n;SFX.tap()});
  on("pick",()=>{if(!sel)return;S.cls=sel;creator(true)});
}
function creator(isNew){
  const L={...S.look};let name=S.name;
  const sw=(key,list,isCol)=>`<div class="sw ${isCol?"":"txt"}" data-key="${key}">${list.map((v,i)=>`<button data-i="${i}" class="${L[key]===v?"on":""}" ${isCol?`style="background:${v}"`:""} aria-label="${key} ${isCol?i+1:v}">${isCol?"":v.toUpperCase()}</button>`).join("")}</div>`;
  modal(`<h2>${isNew?"CREATE YOUR HUNTER":"CHANGE YOUR LOOK"}</h2>
    <div class="creator"><canvas class="pv" id="pv" width="32" height="32"></canvas><div class="rows">
      <div class="optrow"><label for="nm">NAME</label><input class="namein" id="nm" maxlength="10" value="${name}" autocomplete="off" spellcheck="false"></div></div></div>
    <div class="optrow"><label>SKIN</label>${sw("skin",SKINS,true)}</div>
    <div class="optrow"><label>HAIR</label>${sw("hair",HAIRS,false)}</div>
    <div class="optrow"><label>HAIR COLOUR</label>${sw("hairCol",HAIRCOLS,true)}</div>
    <div class="optrow"><label>OUTFIT</label>${sw("outfit",OUTFITS,true)}</div>
    <div class="optrow"><label>EXTRA</label>${sw("acc",ACCS,false)}</div>
    <button class="go wide" id="cdone">${isNew?"START THE HUNT":"SAVE LOOK"}</button>`);
  const pv=$("pv").getContext("2d");
  const draw=()=>{pv.clearRect(0,0,32,32);pv.save();pv.translate(0,2);pv.scale(2,2);drawPerson(pv,0,0,2,L,0,CLASSES[S.cls].badge);pv.restore()};draw();
  const lists={skin:SKINS,hair:HAIRS,hairCol:HAIRCOLS,outfit:OUTFITS,acc:ACCS};
  $("box").querySelectorAll(".sw").forEach(row=>row.querySelectorAll("button").forEach(b=>b.onclick=()=>{const key=row.dataset.key;L[key]=lists[key][+b.dataset.i];row.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));draw();SFX.tap()}));
  on("cdone",()=>{S.look=L;S.name=($("nm").value.trim().toUpperCase().replace(/[^A-Z0-9 ]/g,"")||"HUNTER").slice(0,10);closeModal();
    if(isNew){S.started=true;S.hp=maxHP();say([{s:"PENNY",t:`Nice to meet you, ${S.name}! A ${CLASSES[S.cls].n} with ${CLASSES[S.cls].skill}. That will come in handy.`},
      {s:"PENNY",t:"One quick question first. Some parts of Money Hunters show real offers, and those are for adults only. Are you 18 or over?",choices:[{label:"YES, 18+",fn:()=>{S.age=true;startTown()}},{label:"NO",fn:()=>{S.age=false;startTown()}}]}])}
    else{hud();save();toast("LOOK SAVED")}});
}
function startTown(){MAP=MAPS.town;P.x=P.fx=14;P.y=P.fy=30;P.dir=3;enterWorld(true)}
function enterWorld(tutorial){
  mode="world";introPenny=false;$("topbar").hidden=false;$("controls").hidden=false;$("bpanel").hidden=true;
  if(!tutorial){MAP=MAPS[S.pos.map]||MAPS.town;P.x=P.fx=S.pos.x;P.y=P.fy=S.pos.y;P.dir=S.pos.dir}
  lastZone="";hud();refreshMissions();
  if(tutorial)say([{s:"PENNY",t:S.age?"Thanks! Lessons are open to everyone, and real offers will show up where they're useful.":"No problem! Every lesson is yours. I'll keep real offers out of your way."},
    {s:"PENNY",t:"Use the arrows to walk. Press A to talk to people, read signs and open chests. You can walk into some buildings too."},
    {s:"PENNY",t:"See the sandy path in the middle of the village? Follow it north through the trees to reach Route 1."},
    {s:"PENNY",t:"North is Route 1. Its tall grass is crawling with Scam Goblins, and sometimes a Wild Offer hides in there too. Beat two goblins and the Bank's vault will open."},
    {s:"PENNY",t:"Check the noticeboard next to me every day for a Daily Hunt. Your missions and cards are in the MENU. Good luck!"}],()=>{S.flags.tutorial=true;refreshMissions();emit("talk:penny");save()});
}
document.querySelectorAll(".pad button").forEach(b=>{const d=+b.dataset.d;
  b.addEventListener("pointerdown",e=>{e.preventDefault();held=d;b.classList.add("held");tryMove(d)});
  const up=()=>{if(held===d)held=null;b.classList.remove("held")};b.addEventListener("pointerup",up);b.addEventListener("pointerleave",up);b.addEventListener("pointercancel",up)});
on("abtn",interact);on("menubtn",()=>{if(mode==="world"&&!DQ&&$("ov").hidden)openMenu()});on("mute",()=>{S.muted=!S.muted;hud();save()});
$("ov").addEventListener("click",e=>{if(e.target===$("ov")&&mode==="world")closeModal()});
const KEYS={ArrowUp:0,ArrowRight:1,ArrowDown:2,ArrowLeft:3,w:0,d:1,s:2,a:3};
addEventListener("keydown",e=>{const tag=(e.target.tagName||"").toLowerCase();if(tag==="input")return;
  if(e.key in KEYS&&mode==="world"){e.preventDefault();held=KEYS[e.key];tryMove(held);return}
  if((e.key==="Enter"||e.key===" "||e.key==="z")&&tag!=="button"){if(DQ){e.preventDefault();advance()}else if(mode==="world"&&$("ov").hidden){e.preventDefault();interact()}}
  if(e.key==="Escape"&&!$("ov").hidden&&mode==="world")closeModal();
  if(e.key==="m"&&mode==="world"&&!DQ&&$("ov").hidden)openMenu()});
addEventListener("keyup",e=>{if(e.key in KEYS&&held===KEYS[e.key])held=null});
let last=performance.now();
function loop(t){
  const dt=Math.min(50,t-last);last=t;
  if(DQ&&!DQ.full){DQ.shown+=dt*.05;const l=DQ.lines[DQ.i];$("dtext").textContent=l.t.slice(0,Math.floor(DQ.shown));if(DQ.shown>=l.t.length)finishLine()}
  if(trans){trans.t+=dt;if(trans.kind==="fade"&&!trans.mid&&trans.t>=trans.dur/2){trans.mid=true;trans.cb()}if(trans.t>=trans.dur){const tr=trans;trans=null;if(tr.kind!=="fade")tr.cb()}}
  if(mode==="title")drawTitle(t);else if(mode==="intro")drawIntro(t);
  else if(mode==="world"){if(P.moving){P.mt+=dt/150;if(P.mt>=1){P.mt=1;P.moving=false;arrive()}}if(!P.moving&&held!==null&&!busy())tryMove(held);if(MAP.M)drawWorld(t)}
  else if(mode==="battle"&&B)drawBattle(t,dt);
  if(trans){if(trans.kind==="fade"){const h=trans.dur/2,a=trans.t<h?trans.t/h:1-(trans.t-h)/h;R(0,0,240,208,`rgba(0,0,0,${Math.max(0,Math.min(1,a))})`)}else{const k=Math.floor(trans.t/90)%2;R(0,0,240,208,k?"rgba(0,0,0,.85)":"rgba(255,255,255,.6)")}}
  requestAnimationFrame(loop);
}
(async()=>{
  await Promise.all([loadQuestions().catch(()=>{}),loadMaps().catch(()=>{})]);
  hud();toTitle();
  (document.fonts?document.fonts.load("8px 'Press Start 2P'"):Promise.resolve()).catch(()=>{}).finally(()=>requestAnimationFrame(loop));
})();
window.__g={get S(){return S},get B(){return B},P,get mode(){return mode},get MAP(){return MAP},startBattle,bossFight,interact,advance,openMenu,openBoard,emit,switchSim,goTo,QS,INV,finishAnim,bEnd};
