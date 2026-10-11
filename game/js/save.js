// save.js: Coinsworth player state, XP (shared with the Money Hunters app via mh_xp), missions, daily hunt state.
const DEF=()=>({v:4,started:false,cls:null,name:"HUNTER",look:L_("#e8b48a","short","#2a1f1a","#3f9a4a"),lvl:1,xp:0,hp:30,coins:30,items:{potion:2,superpotion:0,scroll:1},cards:{},powered:{},freed:{},chests:{},flags:{},m:{},notes:{},seen:[],seenInv:[],daily:null,played:{ym:"",n:0},xpTotal:0,age:null,pos:{map:"town",x:12,y:30,dir:0},muted:false});
let S=(()=>{try{const s=JSON.parse(localStorage.getItem("mh_coinsworth")||"null");if(s&&s.v===4)return Object.assign(DEF(),s)}catch(e){}return DEF()})();
const save=()=>{try{S.pos={map:MAP.id,x:P.x,y:P.y,dir:P.dir};localStorage.setItem("mh_coinsworth",JSON.stringify(S))}catch(e){}};
const xpNeed=l=>40*l, maxHP=()=>30+6*(S.lvl-1), atk=()=>8+2*(S.lvl-1), isCls=c=>S.cls===c;
function gainXP(n){if(isCls("scholar"))n=Math.round(n*1.25);S.xp+=n;S.xpTotal=(S.xpTotal||0)+n;try{localStorage.setItem("mh_xp",String(S.xpTotal))}catch(e){}
 let up=false;while(S.xp>=xpNeed(S.lvl)){S.xp-=xpNeed(S.lvl);S.lvl++;up=true}if(up){S.hp=maxHP();setTimeout(()=>{toast(`LEVEL UP! LV ${S.lvl} · HP +6 · ATTACK +2`);SFX.lvl()},400)}return n}
function gainCoins(n){if(isCls("trader"))n=Math.round(n*1.5);S.coins+=n;return n}
const mS=id=>S.m[id]||(S.m[id]={p:0,done:false,on:false});
function refreshMissions(){if(!S.flags.tutorial)return;MISSIONS.forEach(m=>{const st=mS(m.id);if(!m.side&&!st.on&&!st.done&&(!m.after||mS(m.after).done))st.on=true})}
function reward(r){const p=[];if(r.coins)p.push("+"+gainCoins(r.coins)+" coins");if(r.xp)p.push("+"+gainXP(r.xp)+" XP");if(r.item){S.items[r.item]=(S.items[r.item]||0)+1;p.push("+1 "+ITEMS[r.item].n)}return p.join(" · ")}
function emit(ev){
  MISSIONS.forEach(m=>{const st=mS(m.id);if(st.on&&!st.done&&m.ev===ev){st.p++;if(st.p>=m.need){st.done=true;st.on=false;const r=reward(m.rew);setTimeout(()=>toast(`MISSION COMPLETE: ${m.title.toUpperCase()} · ${r}`),200);SFX.win()}}});
  if(ev==="goblin"){const d=daily();if(d.gob<3)d.gob++}
  refreshMissions();hud();save();
}
const today=()=>{const d=new Date();return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")};
const hashStr=s=>{let h=7;for(const ch of s)h=(h*31+ch.charCodeAt(0))|0;return Math.abs(h)};
function daily(){if(!S.daily||S.daily.date!==today()){S.daily={date:today(),gem:false,gob:0,mystery:false,claimed:false,read:false};
  const ym=today().slice(0,7);if(S.played&&S.played.ym===ym)S.played.n++;else S.played={ym,n:1};save()}return S.daily}
const gemSpot=()=>GEM_SPOTS[hashStr(today())%GEM_SPOTS.length];
const weekNo=()=>Math.floor((Date.now()/864e5+3)/7);
