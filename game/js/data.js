// data.js: shared helpers, game content, and the question loader (/data/, network-first).
"use strict";
const SITE="https://moneyhunters.co.uk";
const guideURL=id=>`${SITE}/app.html?guide=${id}`;
const $=id=>document.getElementById(id);
const TS=16,VW=15,VH=13;
const rnd=n=>Math.random()*n|0;
const pick=a=>a[rnd(a.length)];
const shuffle=a=>{for(let i=a.length-1;i>0;i--){const j=rnd(i+1);[a[i],a[j]]=[a[j],a[i]]}return a};
function grid(w,h,c){return[...Array(h)].map(()=>Array(w).fill(c))}
const fill=(M,x,y,w,h,c)=>{for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)if(M[j]&&M[j][i]!==undefined)M[j][i]=c};
const L_=(skin,hair,hairCol,outfit,acc="none")=>({skin,hair,hairCol,outfit,acc});
/* =========================================================
   QUESTION BANK: loaded from /data/ (same origin, network-first)
   ========================================================= */
const QS=[],INV=[];
async function loadQuestions(){
  let questions=[],investigations=[];
  const F=async u=>{try{const r=await fetch(u+"?v="+Date.now());return r.ok?await r.json():null}catch(e){return null}};
  const idx=await F("/data/questions/index.json");
  if(idx&&idx.files){
    const parts=await Promise.all(Object.values(idx.files).map(f=>F("/data/questions/"+f)));
    for(const p of parts)if(p&&p.questions)questions=questions.concat(p.questions);
    const inv=await F("/data/questions/investigations.json");
    if(inv&&inv.investigations)investigations=inv.investigations;
  }
  if(!questions.length){
    const legacy=await F("/data/questions.json");
    if(legacy){questions=legacy.questions||[];investigations=legacy.investigations||investigations}
  }
  for(const x of questions)QS.push({id:x.id,tag:x.topic,tier:x.difficulty,t:x.type==="calc"?"deal":"mc",q:x.question,o:x.options,a:x.answer,e:x.explanation,learn:x.learn_more});
  for(const x of investigations)INV.push({id:x.id,src:x.source,parts:x.parts.map(p=>({s:p.text,f:p.flag,w:p.why})),e:x.explanation,learn:x.learn_more});
}
const WEEKLY_GUIDES={"Bank switching":"pb-bank-switch-bonuses","Cashback sites":"pb-cb-sites","Free shares":"pb-inv-free-shares","Gift card stacking":"pb-cb-giftcards","Survey and app rewards":"pb-side-surveys"};
const CLASSES={
 scout:{n:"SCOUT",badge:"#e8b83a",skill:"Sharp Eyes",d:"Spots hidden items from far away, finds more loot in tall grass, and can always run from wild battles."},
 detective:{n:"DETECTIVE",badge:"#d8c08a",skill:"Red-Flag Sense",d:"In Investigate, one red flag is revealed for free, and investigations hit 20% harder."},
 trader:{n:"TRADER",badge:"#ffc94a",skill:"Haggler",d:"20% off in shops, 50% more coins from battles, and 8 extra seconds on Money Maths questions."},
 scholar:{n:"SCHOLAR",badge:"#f3f0ff",skill:"Bookworm",d:"One free 50/50 in every battle, and 25% more XP from everything."}
};
const SKINS=["#f6d3b3","#e8b48a","#c68a5e","#8d5a3b","#5a3a28"];
const HAIRS=["short","long","spiky","bun"];
const HAIRCOLS=["#2a1f1a","#5a3a1a","#c8902a","#e8d070","#b8283c","#4a5ad8"];
const OUTFITS=["#3f9a4a","#3a5aa8","#8a5a2a","#7a4ac8","#c8504a","#2b2f3a"];
const ACCS=["none","glasses","cap","headphones"];
const ITEMS={potion:{n:"Potion",d:"Restores 15 HP.",p:15,heal:15},superpotion:{n:"Super Potion",d:"Restores 40 HP.",p:35,heal:40},scroll:{n:"50/50 Scroll",d:"Removes one wrong answer in a quiz.",p:25}};
const CARDS={
 switch:{n:"Switch Bonus",type:"offer",r:"C",icon:"£",tag:"banking",guide:"pb-bank-switch-bonuses",gname:"bank switch guide",t:"Banks pay you to move your current account. Check the pay-in amount, Direct Debits and deadline.",pt:"Keep the new account open until the bonus lands, and look for any clawback clause."},
 freeshare:{n:"Free Share",type:"offer",r:"C",icon:"↗",tag:"investing",guide:"pb-inv-free-shares",gname:"free shares guide",t:"Trading apps give you a share for signing up. Its value can go down as well as up.",pt:"Check for a minimum holding period before you sell."},
 cashback:{n:"Cashback Bonus",type:"offer",r:"C",icon:"%",tag:"cashback",guide:"pb-cb-sites",gname:"cashback guide",t:"Cashback sites pay back part of what you spend at partner shops.",pt:"Cashback can take weeks to confirm. Don't count it until it's paid."},
 giftcard:{n:"Gift Card Deal",type:"offer",r:"C",icon:"▣",tag:"shopping",guide:"pb-cb-giftcards",gname:"gift card guide",t:"Discounted gift cards save you money at shops you already use.",pt:"Only buy gift cards for shops you'll definitely spend at."},
 survey:{n:"Survey Bonus",type:"offer",r:"C",icon:"✎",tag:"side",guide:"pb-side-surveys",gname:"surveys guide",t:"Survey sites sometimes add a sign-up bonus. They should never charge you to join.",pt:"Check the minimum cash-out before you put the time in."},
 referral:{n:"Refer-a-Friend",type:"offer",r:"C",icon:"♥",tag:"side",guide:"pb-side-referrals",gname:"referrals guide",t:"Referral schemes reward you when a friend joins. Often the friend gets a bonus too.",pt:"Only refer people to things you'd genuinely recommend."},
 switchpro:{n:"Switch Pro",type:"skill",r:"R",icon:"✓",t:"You aced the bank switch simulator: full switch, active Direct Debits, external pay-in, and no early closure."},
 cass:{n:"CASS Shield",type:"boss",r:"R",icon:"C",t:"The Current Account Switch Service moves everything in 7 working days, and the Switch Guarantee covers you if it goes wrong."},
 overdraft:{n:"Overdraft Truth",type:"boss",r:"L",icon:"!",t:"At around 40% interest, every £500 you stay overdrawn for a year costs about £200."},
 unit:{n:"Unit Price Lens",type:"boss",r:"R",icon:"%",t:"The price per kg, litre or item on the shelf label shows the real best value."},
 stacker:{n:"Master Stacker",type:"boss",r:"L",icon:"$",t:"Cashback, a discounted gift card and loyalty points can all apply to the same shop."}
};
const OFFER_IDS=["switch","freeshare","cashback","giftcard","survey","referral"];
const GOBLINS=[
 {n:"Phishing Goblin",tags:["scams"],col:"#5aa84a",item:"phone",weak:"investigate"},
 {n:"Fee Goblin",tags:["banking","credit"],col:"#c8504a",item:"coin",weak:"attack"},
 {n:"Hype Goblin",tags:["investing","scams"],col:"#8a5ad8",item:"rocket",weak:"investigate"},
 {n:"Shrink Goblin",tags:["shopping","cashback"],col:"#e8792a",item:"box",weak:"attack"},
 {n:"Survey Goblin",tags:["side","budgeting"],col:"#d04a8a",item:"clip",weak:"investigate"}
];
const BOSSES={
 bank:{n:"Overdraft Ogre",spr:"ogre",lv:6,hp:95,atk:7,tags:["banking","credit","saving"],tier:2,xp:90,coins:60,weak:"investigate",
       taunt:"Your fees are MINE! Every pound you forget about feeds me!",lose:"Nooo... you actually read the terms!",
       p2:"The Overdraft Ogre is furious! FEE STORM incoming. Questions get harder!",moves:["Overdraft Slam","Hidden Charge","Fee Storm"],cards:["cass","overdraft"],guide:"pb-bank-overdrafts",gname:"overdraft guide",bg:["#26355e","#34477a"]},
 market:{n:"Shrinkflation Sam",spr:"sam",lv:8,hp:115,atk:8,tags:["shopping","cashback","budgeting"],tier:2,xp:110,coins:70,weak:"attack",
       taunt:"Same price, smaller pack. You'll never notice. Heh heh.",lose:"You checked the price per kilo...",
       p2:"Sam fires his SHRINK RAY! Your answer timer shrinks!",moves:["Shrink Ray","Price Creep","Tiny Pack Toss"],cards:["unit","stacker"],guide:"pb-shop-unit-price",gname:"unit price guide",bg:["#5a321e","#6e4024"]}
};
const MISSIONS=[
 {id:"m1",title:"First steps",desc:"Meet Penny outside her lab.",ev:"talk:penny",need:1,rew:{coins:20,xp:10}},
 {id:"m2",title:"Goblin trouble",desc:"Beat 2 Scam Goblins in Route 1's tall grass.",ev:"goblin",need:2,rew:{coins:30,xp:30},after:"m1"},
 {id:"m3",title:"Catch a deal",desc:"Catch a Wild Offer in the tall grass.",ev:"catch",need:1,rew:{coins:20,xp:20,item:"potion"},after:"m1"},
 {id:"m4",title:"Free the Bank",desc:"Go into Coinsworth Bank in Market Square and beat the Overdraft Ogre in the vault.",ev:"boss:bank",need:1,rew:{coins:60,xp:60},after:"m2"},
 {id:"m5",title:"Free the Market",desc:"Defeat Shrinkflation Sam in Market Square.",ev:"boss:market",need:1,rew:{coins:60,xp:60},after:"m4"},
 {id:"s1",title:"Rosa's lost purse",desc:"Rosa dropped her purse in the long grass on Route 1. Find it and bring it back.",ev:"purse",need:1,rew:{coins:40,xp:30},side:true},
 {id:"s2",title:"Switch training",desc:"Talk to Clara in Coinsworth Bank and complete the switch simulator.",ev:"sim",need:1,rew:{coins:20,xp:20},side:true}
];
const TIPS=["Before any switch offer, write down the deadline and set a reminder a week early.","Check the unit price on shelf labels. Bigger packs aren't always cheaper.","Forward scam texts to 7726. It's free and helps networks block them.","Cashback can take weeks to confirm. Don't spend it until it's paid.","Free shares can fall in value. Check any minimum holding period before selling."];
const WEEKLY=["Bank switching","Cashback sites","Free shares","Gift card stacking","Survey and app rewards"];
