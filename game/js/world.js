// world.js: maps (Tiled .tmj), town + bank drawing, movement, NPCs, dialog, switch simulator.

const MAPS={
 town:{id:"town",w:40,h:36,M:null,grass:true,
  blds:[
   {id:"home",x:3,y:26,w:4,h:3,roof:"#c4524a",wall:"#f1e3cf",label:"HOME"},
   {id:"lab",x:11,y:26,w:6,h:3,roof:"#4a7bd0",wall:"#e8eef8",label:"PENNY'S LAB"},
   {id:"mart",x:24,y:26,w:5,h:3,roof:"#2f9e7a",wall:"#e1efe7",label:"MART"},
   {id:"bank",x:4,y:3,w:6,h:4,roof:"#3a5aa8",wall:"#d9dff2",label:"BANK"},
   {id:"market",x:14,y:3,w:7,h:4,roof:"#e0703a",wall:"#f6e6d6",label:"MARKET"},
   {id:"exchange",x:25,y:3,w:7,h:4,roof:"#6a6a7a",wall:"#d6d6de",label:"EXCHANGE"}],
  npcs:[
   {id:"penny",x:12,y:29,dir:2,name:"PENNY",look:L_("#f2c7a0","bun","#c8c8d0","#7a4ac8","glasses")},
   {id:"dee",x:30,y:31,dir:2,name:"DEE",look:L_("#c68a5e","long","#3a2a1a","#e0703a")},
   {id:"tom",x:9,y:31,dir:1,name:"TOM",look:L_("#f2c7a0","short","#e8c070","#4aa0a0")},
   {id:"rosa",x:23,y:17,dir:2,name:"ROSA",look:L_("#e8b48a","bun","#e8e8e8","#c45a8a")},
   {id:"leo",x:8,y:17,dir:2,name:"LEO",look:L_("#8d5a3b","spiky","#2a1f1a","#e8b83a")},
   {id:"mo",x:12,y:8,dir:2,name:"MO",look:L_("#c68a5e","short","#1b1f3a","#2f9e7a","cap")}],
  signs:[
   {x:7,y:2,text:["SCAM SWAMP","Phishers and fraudsters lurk beyond this gate. Coming soon!"]},
   {x:32,y:2,text:["ARCADE PARK","Loot Box Larry's playground. Coming soon!"]},
   {x:22,y:14,text:["ROUTE 1","Tall grass ahead: Scam Goblins and Wild Offers!","↑ Market Square   ↓ Hunter's Village"]},
   {x:22,y:26,text:["HUNTER'S VILLAGE","Every Money Hunter starts here.","↑ The road north leads to Route 1 and Market Square."]}],
  board:{x:17,y:29},cart:{x:31,y:31},
  chests:[{id:"c1",x:2,y:22,item:"superpotion"},{id:"c2",x:36,y:11,item:"scroll"},{id:"c3",x:35,y:29,coins:30}]},
 bank:{id:"bank",w:12,h:10,grass:false,
  M:["wwwwwVVwwwww","woooooooooow","wccccooccccw","woooooooooow","woorrrrrroow","wPorrrrrroPw","woooooooooow","wbboooooobbw","woooooooooow","wwwwwddwwwww"].map(r=>r.split("")),
  blds:[],
  npcs:[
   {id:"clara",x:2,y:1,dir:2,name:"CLARA",look:L_("#e8b48a","long","#2a1f1a","#3a5aa8")},
   {id:"ben",x:9,y:1,dir:2,name:"BEN",look:L_("#5a3a28","short","#1b1f3a","#2f9e7a","glasses")},
   {id:"ivy",x:8,y:6,dir:3,name:"IVY",look:L_("#f6d3b3","long","#c8902a","#c8504a")}],
  signs:[],board:null,cart:null,chests:[]}
};
MAPS.town.blds.forEach(b=>{b.dx=b.x+Math.floor(b.w/2);b.dy=b.y+b.h-1});
const PURSE={x:28,y:21};
const GEM_SPOTS=[[5,14],[33,14],[9,21],[30,22],[2,16],[36,17],[26,15],[6,22]];
let MAP=MAPS.town;
function solid(x,y){
  const m=MAP;if(x<0||y<0||x>=m.w||y>=m.h)return true;
  if("T~fGwcPbVd".includes(m.M[y][x]))return true;
  if(m.blds.some(b=>x>=b.x&&x<b.x+b.w&&y>=b.y&&y<b.y+b.h))return true;
  if(m.npcs.some(n=>n.x===x&&n.y===y)||m.signs.some(s=>s.x===x&&s.y===y))return true;
  if(m.board&&m.board.x===x&&m.board.y===y)return true;
  if(m.cart&&m.cart.x===x&&m.cart.y===y)return true;
  return m.chests.some(c=>c.x===x&&c.y===y);
}
const zoneOf=y=>MAP.id==="bank"?"COINSWORTH BANK":y<=11?"MARKET SQUARE":y<=23?"ROUTE 1":"HUNTER'S VILLAGE";

const LEGENDS={};
const chunks=(a,n)=>Array.from({length:Math.ceil(a.length/n)},(x,i)=>a.slice(i*n,i*n+n));
async function loadMaps(){
  for(const id of ["town","bank"]){
    try{
      const res=await fetch(`/game/maps/${id}.tmj?v=`+Date.now());if(!res.ok)throw 0;
      const m=await res.json();
      const legend=(m.tilesets[0].properties||[]).find(p=>p.name==="legend").value;
      LEGENDS[id]=legend;
      MAPS[id].M=chunks(m.layers[0].data,m.width).map(row=>row.map(g=>legend[g-1]||"."));
    }catch(e){}
  }
  MAP=MAPS.town;
}

const cv=$("cv"),c=cv.getContext("2d");c.imageSmoothingEnabled=false;
function R(x,y,w,h,col,ctx=c){ctx.fillStyle=col;ctx.fillRect(x,y,w,h)}
function txt(s,x,y,size,col,align="left",ctx=c){ctx.font=`${size}px 'Press Start 2P', monospace`;ctx.textAlign=align;ctx.textBaseline="top";ctx.fillStyle=col;ctx.fillText(s,x,y)}
function drawPerson(ctx,X,Y,dir,L,step=0,badge){
  const r=(x,y,w,h,col)=>R(X+x,Y+y,w,h,col,ctx),H=L.hairCol;
  r(4,14,8,2,"rgba(0,0,0,.25)");r(5,11,2,4-step,"#2b2f5a");r(9,11,2,3+step,"#2b2f5a");
  r(4,7,8,5,L.outfit);if(badge)r(4,7,8,1,badge);r(3,8,1,3,L.outfit);r(12,8,1,3,L.outfit);
  r(5,2,6,6,L.skin);r(4,1,8,3,H);
  if(L.hair==="long"){if(dir===0)r(4,2,8,7,H);else{r(4,2,1,7,H);r(11,2,1,7,H)}}
  if(L.hair==="spiky"){r(4,0,1,1,H);r(6,-1,1,2,H);r(9,-1,1,2,H);r(11,0,1,1,H)}
  if(L.hair==="bun")r(7,-1,2,2,H);
  if(dir===0)r(4,2,8,5,H);
  else if(dir===2){r(6,5,1,1,"#1b1f3a");r(9,5,1,1,"#1b1f3a")}
  else if(dir===1){r(9,5,1,1,"#1b1f3a");r(4,2,2,4,H)}
  else{r(6,5,1,1,"#1b1f3a");r(10,2,2,4,H)}
  if(L.acc==="glasses"&&dir!==0){if(dir===2){r(5,4,3,2,"#1b1f3a");r(8,4,3,2,"#1b1f3a");r(6,4,1,1,"#9fd0f5");r(9,4,1,1,"#9fd0f5")}else if(dir===1)r(8,4,3,2,"#1b1f3a");else r(5,4,3,2,"#1b1f3a")}
  if(L.acc==="cap"){r(4,0,8,2,"#c8504a");if(dir===2)r(4,2,8,1,"#a03a34");else if(dir===1)r(10,2,4,1,"#a03a34");else if(dir===3)r(2,2,4,1,"#a03a34")}
  if(L.acc==="headphones"){r(4,-1,8,1,"#222");r(3,3,1,3,"#222");r(12,3,1,3,"#222")}
}
const drawPlayer=(ctx,X,Y,dir,step)=>drawPerson(ctx,X,Y,dir,S.look,step,CLASSES[S.cls||"scout"].badge);

function drawTile(x,y,X,Y,t){
  const g=MAP.M[y][x],ck=(x+y)%2;
  const grass=()=>{R(X,Y,16,16,ck?"#6cc06a":"#66b864");if((x*7+y*13)%5===0){R(X+4,Y+4,1,2,"#4f9e52");R(X+11,Y+10,1,2,"#4f9e52")}};
  const floor=()=>R(X,Y,16,16,ck?"#d8d2c4":"#cfc8b8");
  switch(g){
  case ".":grass();return;
  case ",":R(X,Y,16,16,"#d8c08a");if((x*3+y*5)%4===0){R(X+3,Y+5,2,2,"#c4aa74");R(X+11,Y+11,2,1,"#c4aa74")}return;
  case "P":floor();R(X+4,Y+10,8,6,"#a0602a");R(X+3,Y+2,10,9,"#2f8a4a");R(X+5,Y+3,3,3,"#46a860");return;
  case "p":    R(X,Y,16,16,"#c9c2b4");R(X,Y,16,1,"#b3ab9c");R(X,Y,1,16,"#b3ab9c");R(X+8,Y+8,8,1,"#bdb5a6");return;
  case '"':{R(X,Y,16,16,"#4aa553");const s=Math.round(Math.sin(t/450+x*.7+y));
    for(let k=0;k<4;k++){const bx=X+1+k*4+s,by=Y+(k%2?6:2);R(bx,by+3,1,6,"#2c7a38");R(bx+1,by+1,1,6,"#3a8f45");R(bx+2,by+3,1,6,"#2c7a38")}
    for(let k=0;k<3;k++){const bx=X+3+k*5-s,by=Y+10;R(bx,by,1,5,"#2c7a38");R(bx+1,by-2,1,6,"#5fbf68")}return}
  case "T":grass();R(X+6,Y+11,4,5,"#7a4e2a");R(X+2,Y+1,12,10,"#2f8a4a");R(X+1,Y+3,14,6,"#2f8a4a");R(X+4,Y+2,4,3,"#46a860");R(X+3,Y+8,10,2,"#25703c");return;
  case "~":{R(X,Y,16,16,"#4a9ad8");const o=Math.floor(t/350+x+y)%4;R(X+2+o*2,Y+4,5,1,"#9fd0f5");R(X+8-o,Y+11,5,1,"#9fd0f5");return}
  case "F":{grass();const s=Math.round(Math.sin(t/500+x));R(X+3+s,Y+4,2,2,"#ff6a7a");R(X+10,Y+8+s,2,2,"#ffd84a");R(X+6-s,Y+11,2,2,"#ff9ad8");R(X+4,Y+6,1,3,"#2f8a4a");R(X+11,Y+10,1,3,"#2f8a4a");return}
  case "f":grass();R(X+2,Y+5,2,9,"#a8743a");R(X+12,Y+5,2,9,"#a8743a");R(X,Y+7,16,2,"#c08a4a");R(X,Y+11,16,2,"#c08a4a");return;
  case "G":R(X,Y,16,16,"#3a3050");R(X+2,Y+3,12,13,"#15101f");R(X,Y+6,16,1,"#7a7a8a");R(X,Y+10,16,1,"#7a7a8a");R(X+6,Y+7,4,4,"#ffc94a");R(X+7,Y+5,2,3,"#ffc94a");return;
  case "w":R(X,Y,16,16,"#2c3a66");R(X,Y+10,16,6,"#3a4a80");R(X,Y+10,16,1,"#6a7ac0");
    if(y===0&&(x===2||x===9)){R(X+1,Y+1,14,9,"#f6f1e3");R(X+2,Y+2,12,2,"#3a5aa8");R(X+3,Y+5,10,1,"#c8504a");R(X+3,Y+7,7,1,"#8a8fc0")}return;
  case "o":floor();return;
  case "c":floor();R(X,Y+1,16,13,"#8a5a2a");R(X,Y+1,16,3,"#b07a3a");R(X,Y+13,16,1,"#5a3a1a");return;
  case "r":R(X,Y,16,16,"#b8283c");R(X+2,Y+2,12,12,"#c43c4c");R(X+6,Y+6,4,4,"#ffc94a");return;
  case "b":floor();R(X+1,Y+6,14,4,"#8a5a2a");R(X+1,Y+6,14,1,"#b07a3a");R(X+2,Y+10,2,4,"#5a3a1a");R(X+12,Y+10,2,4,"#5a3a1a");return;
  case "V":{R(X,Y,16,16,"#4a4a5a");c.fillStyle="#8a8a9a";c.beginPath();c.arc(x===5?X+16:X,Y+9,12,0,7);c.fill();c.fillStyle="#6a6a7a";c.beginPath();c.arc(x===5?X+16:X,Y+9,7,0,7);c.fill();
    const locked=!mS("m2").done;R(x===5?X+13:X-3,Y+1,6,3,locked?"#ff4f6d":"#5fd38d");return}
  case "d":R(X,Y,16,16,"#2c3a66");R(X+1,Y+3,15,13,"#a0602a");R(X+2,Y+5,13,9,"#c07a3a");return;
  }
}
function drawBuilding(b,cx,cy,t){
  const X=b.x*TS-cx,Y=b.y*TS-cy,W=b.w*TS,H=b.h*TS;if(X>240||Y>208||X+W<0||Y+H<-16)return;
  R(X+2,Y+12,W-4,H-12,b.wall);R(X+2,H+Y-3,W-4,3,"rgba(0,0,0,.15)");R(X,Y,W,15,b.roof);R(X,Y+13,W,2,"rgba(0,0,0,.2)");
  if(b.id==="home")R(X+6,Y-5,4,6,"#8a3a30");
  if(b.id==="lab"){R(X+W-12,Y-8,2,8,"#888");R(X+W-16,Y-10,10,3,"#bbb")}
  if(b.id==="market")for(let i=0;i<W;i+=6)R(X+i,Y+15,3,4,(i/6)%2?"#fff":"#d84a3a");
  if(b.id==="bank")for(let i=6;i<W-4;i+=12)R(X+i,Y+18,3,H-21,"#f6f8ff");
  for(let i=1;i<b.w;i+=2){if(b.x+i===b.dx)continue;R(X+i*TS-4,Y+22,8,7,b.id==="exchange"?"#8a8a96":"#7fb8e6");R(X+i*TS-4,Y+22,8,2,"#a8d4f2")}
  const dX=b.dx*TS-cx;R(dX+3,Y+H-14,10,14,"#6b3f22");R(dX+10,Y+H-8,1,2,"#ffc94a");
  if(b.id==="exchange"){R(dX-2,Y+H-22,20,7,"#c43c3c");txt("CLOSED",dX+8,Y+H-21,4,"#fff","center")}
  txt(b.label,X+W/2,Y+4,6,"#fff","center");
  if(BOSSES[b.id]){const mx=X+W-8,bob=Math.round(Math.sin(t/220+b.x));
    if(S.freed[b.id]){R(mx,Y-8,1,11,"#eee");R(mx+1,Y-8,7,5,"#5fd38d")}else{R(mx-1,Y-11+bob,7,9,"#ff4f6d");R(mx+2,Y-9+bob,1,4,"#fff");R(mx+2,Y-4+bob,1,1,"#fff")}}
}
function drawObj(o,X,Y,t){
  if(o.k==="npc"){drawPerson(c,X,Y,o.n.dir,o.n.look,0);return}
  if(o.k==="player"){drawPlayer(c,X,Y,P.dir,P.moving?(Math.floor(P.mt*2)%2):0);return}
  if(o.k==="sign"){R(X+7,Y+9,2,7,"#7a4e2a");R(X+2,Y+3,12,7,"#a8743a");R(X+3,Y+4,10,1,"#d8b070");R(X+4,Y+6,8,1,"#6b4420");return}
  if(o.k==="board"){R(X+3,Y+11,2,5,"#7a4e2a");R(X+11,Y+11,2,5,"#7a4e2a");R(X+1,Y+2,14,10,"#a8743a");R(X+2,Y+3,12,8,"#efe3c0");R(X+3,Y+4,4,4,"#fff");R(X+9,Y+5,4,3,"#ffd84a");
    if(!daily().claimed&&S.flags.tutorial){const bob=Math.round(Math.sin(t/200)*1.5);R(X+6,Y-8+bob,4,7,"#ff4f6d");R(X+7,Y-7+bob,2,3,"#fff");R(X+7,Y-3+bob,2,1,"#fff")}return}
  if(o.k==="cart"){R(X+1,Y+7,14,6,"#a0602a");R(X+2,Y+13,3,3,"#3a2a1a");R(X+11,Y+13,3,3,"#3a2a1a");R(X+1,Y+3,1,5,"#7a4e2a");R(X+14,Y+3,1,5,"#7a4e2a");for(let i=0;i<16;i+=4){R(X+i,Y,2,4,"#ff6470");R(X+i+2,Y,2,4,"#fff")}R(X+4,Y+8,3,3,"#ffc94a");R(X+9,Y+8,3,3,"#5fd38d");return}
  if(o.k==="chest"){if(S.chests[o.ch.id]){R(X+2,Y+7,12,7,"#a0602a");R(X+3,Y+8,10,4,"#3a2010");R(X+2,Y+3,12,4,"#c07a3a")}else{R(X+2,Y+5,12,9,"#a0602a");R(X+2,Y+5,12,3,"#c07a3a");R(X+2,Y+9,12,1,"#7a4420");R(X+7,Y+8,2,3,"#ffc94a")}return}
  if(o.k==="spark"){const a=(Math.sin(t/150+o.x)+1)/2;c.globalAlpha=.4+a*.6;R(X+7,Y+3,2,10,o.col);R(X+3,Y+7,10,2,o.col);R(X+6,Y+6,4,4,o.col);c.globalAlpha=1}
}
const SPR={
 ogre(ctx){const B="#6f9a52",D="#4d7038",r=(x,y,w,h,col)=>R(x,y,w,h,col,ctx);
  r(-12,14,8,8,D);r(4,14,8,8,D);r(-18,-14,36,30,B);r(-14,-22,28,10,B);r(-14,-28,4,8,"#efe6d0");r(10,-28,4,8,"#efe6d0");
  r(-10,-14,7,5,"#fff");r(3,-14,7,5,"#fff");r(-9,-13,3,3,"#1b1f3a");r(3,-13,3,3,"#1b1f3a");r(-11,-17,8,2,D);r(3,-17,8,2,D);
  r(-9,-4,18,5,"#3a1a1a");r(-7,-4,2,2,"#fff");r(5,-4,2,2,"#fff");r(-3,4,6,12,"#c43c3c");r(-4,3,8,3,"#a02a2a");r(-24,-8,6,16,B);r(18,-10,6,14,B);r(-34,-20,14,9,"#d04040");r(-32,-17,10,2,"#ffc94a")},
 sam(ctx,t){const r=(x,y,w,h,col)=>R(x,y,w,h,col,ctx),s=(t/450|0)%3;
  r(-36,8+s*2,10-s*2,14-s*3,"#e8792a");r(26,12+s,8-s,10-s*2,"#e8792a");r(-6,16,3,7,"#5a3a20");r(3,16,3,7,"#5a3a20");
  r(-14,-26,28,42,"#e8792a");r(-14,-26,28,4,"#c45e18");r(-10,-20,20,12,"#fff3c4");r(-7,-17,14,2,"#c43c3c");r(-5,-13,10,2,"#c43c3c");
  r(-8,-2,5,5,"#fff");r(3,-2,5,5,"#fff");r(-8,0,2,2,"#1b1f3a");r(3,0,2,2,"#1b1f3a");r(-9,-5,6,2,"#8a3a10");r(3,-5,6,2,"#8a3a10");r(-4,7,8,2,"#1b1f3a");r(-6,5,2,2,"#1b1f3a");r(-20,0,6,4,"#e8792a");r(14,0,6,4,"#e8792a")},
 goblin(ctx,t,g){const r=(x,y,w,h,col)=>R(x,y,w,h,col,ctx),col=g.col;
  r(-8,10,6,5,col);r(2,10,6,5,col);r(-10,-6,20,17,col);r(-12,-15,24,11,col);r(-19,-17,7,5,col);r(12,-17,7,5,col);r(-21,-19,3,3,col);r(18,-19,3,3,col);
  r(-7,-12,5,4,"#ffe14a");r(2,-12,5,4,"#ffe14a");r(-7,-11,2,2,"#1b1f3a");r(2,-11,2,2,"#1b1f3a");r(-6,-6,12,2,"#1b1f3a");r(-4,-6,2,2,"#fff");r(2,-6,2,2,"#fff");r(-5,0,10,7,"rgba(255,255,255,.22)");
  const it=g.item,ix=-19;
  if(it==="phone"){r(ix,-6,7,11,"#222");r(ix+1,-5,5,7,"#4ad0ff")}
  if(it==="coin"){r(ix,-3,7,7,"#ffc94a");r(ix+2,-2,2,5,"#b8861a")}
  if(it==="rocket"){r(ix+1,-12,5,12,"#eee");r(ix+1,-14,5,3,"#e04848");r(ix+2,0,3,2+((t/90|0)%2)*2,"#ffc94a")}
  if(it==="box"){r(ix,-4,8,9,"#e8792a");r(ix+1,-3,6,3,"#fff3c4")}
  if(it==="clip"){r(ix,-6,8,11,"#c89a5a");r(ix+1,-4,6,8,"#fff")}},
 offer(ctx,t,g){const r=(x,y,w,h,col)=>R(x,y,w,h,col,ctx),y=Math.round(Math.sin(t/300)*3);
  ctx.globalAlpha=.25+.15*Math.sin(t/200);r(-20,-30+y,40,52,"#ffc94a");ctx.globalAlpha=1;r(-14,-26+y,28,40,"#ffc94a");r(-12,-24+y,24,36,"#2d3366");txt(CARDS[g.card].icon,0,-12+y,12,"#ffc94a","center",ctx);
  for(let i=0;i<4;i++){const a=t/400+i*1.57;r(Math.round(Math.cos(a)*24),Math.round(Math.sin(a)*24)+y-6,2,2,"#fff")}}
};

const P={x:12,y:30,dir:0,moving:false,mt:0,fx:12,fy:30};
let bumps=0,mode="title",held=null,steps=0,sinceBattle=99,lastZone="",trans=null,rustles=[];
const busy=()=>mode!=="world"||!!DQ||!$("ov").hidden||!!trans;
const DIRS=[[0,-1],[1,0],[0,1],[-1,0]];
function goTo(mapId,x,y,dir){trans={kind:"fade",t:0,dur:500,mid:false,cb:()=>{MAP=MAPS[mapId];P.x=P.fx=x;P.y=P.fy=y;P.dir=dir;P.moving=false;lastZone="";save()}}}
function tryMove(d){
  if(busy()||P.moving)return;
  P.dir=d;const [dx,dy]=DIRS[d],nx=P.x+dx,ny=P.y+dy;
  const door=MAP.blds.find(b=>b.dx===nx&&b.dy===ny);if(door){enterBuilding(door.id);return}
  const t=MAP.M[ny]&&MAP.M[ny][nx];
  if(t==="G"){say(["The gate is chained shut. A new area is coming soon!"]);return}
  if(t==="d"){goTo("town",7,7,2);return}
  if(t==="V"){vault();return}
  if(solid(nx,ny)){SFX.bump();bumps++;if(bumps>=4&&MAP.id==="town"&&P.y>=24){bumps=0;banner("ROUTE 1 IS UP THE MIDDLE PATH ↑")}return}
  bumps=0;
  P.fx=P.x;P.fy=P.y;P.x=nx;P.y=ny;P.moving=true;P.mt=0;
}
function arrive(){
  steps++;sinceBattle++;
  const z=zoneOf(P.y);if(z!==lastZone){lastZone=z;banner(z)}
  if(MAP.id!=="town"){if(steps%5===0)save();return}
  const g=gemSpot(),d=daily();
  if(!d.gem&&P.x===g[0]&&P.y===g[1]&&(d.read||isCls("scout"))){d.gem=true;const n=gainCoins(15);SFX.win();say([`You found today's hidden gem! +${n} coins. Daily Hunt task done.`]);hud();save();return}
  if(!S.flags.purse&&P.x===PURSE.x&&P.y===PURSE.y&&mS("s1").on){S.flags.purse=true;SFX.coin();say(["You found a purple purse with a name tag: ROSA. Better take it back to her."]);save();return}
  if(MAP.M[P.y][P.x]==='"'){rustles.push({x:P.x,y:P.y,t:0});SFX.grass();if(sinceBattle>=3&&Math.random()<.14){sinceBattle=0;encounter()}}
  if(steps%5===0)save();
}
function encounter(){
  const r=Math.random(),itemRate=isCls("scout")?.2:.12;
  if(r<itemRate){const n=gainCoins(5+rnd(6));SFX.coin();say([`Something glinted in the grass... you found ${n} coins!`]);hud();return}
  SFX.alert();
  if(r<itemRate+.28){const card=pick(OFFER_IDS);startBattle("offer",{n:CARDS[card].n,card,tag:CARDS[card].tag,spr:"offer",lv:"?",tier:1})}
  else{const g=pick(GOBLINS),lv=2+rnd(3)+Object.keys(S.freed).length*2;startBattle("wild",{...g,spr:"goblin",lv,hp:16+lv*3,max:16+lv*3,atk:3+lv,tier:S.lvl>=3?2:1,xp:12+lv*3,coins:6+lv*2,moves:["Sneaky Fee","Fake Link","Pressure Tactic","Fine Print"]})}
}
function facing(){const [dx,dy]=DIRS[P.dir];return[P.x+dx,P.y+dy]}
function interact(){
  if(DQ){advance();return}
  if(busy())return;
  let [fx,fy]=facing();
  if(MAP.M[fy]&&MAP.M[fy][fx]==="c"){const [dx,dy]=DIRS[P.dir];fx+=dx;fy+=dy}
  const n=MAP.npcs.find(n=>n.x===fx&&n.y===fy);if(n){n.dir=(P.dir+2)%4;talk(n.id);return}
  if(MAP.cart&&MAP.cart.x===fx&&MAP.cart.y===fy){talk("dee");return}
  const s=MAP.signs.find(s=>s.x===fx&&s.y===fy);if(s){say(s.text);return}
  if(MAP.board&&MAP.board.x===fx&&MAP.board.y===fy){openBoard();return}
  const ch=MAP.chests.find(c=>c.x===fx&&c.y===fy);if(ch){openChest(ch);return}
  const b=MAP.blds.find(b=>b.dx===fx&&b.dy===fy);if(b){enterBuilding(b.id);return}
  const t=MAP.M[fy]&&MAP.M[fy][fx];if(t==="V")vault();
}
function openChest(ch){
  if(S.chests[ch.id]){say(["The chest is empty."]);return}
  S.chests[ch.id]=true;SFX.win();
  if(ch.coins)say([`You opened the chest. ${gainCoins(ch.coins)} coins inside!`]);
  else{S.items[ch.item]=(S.items[ch.item]||0)+1;say([`You opened the chest and found a ${ITEMS[ch.item].n}!`])}
  hud();save();
}
function heal(){S.hp=maxHP();hud();save()}
function talk(id){
  const n=S.name;
  if(id==="penny"){const L=[];
    if(!mS("m2").done)L.push(`North of here is Route 1, ${n}. Beat two Scam Goblins in the tall grass. Phishing Goblins hate INVESTIGATE, by the way.`);
    else if(!S.freed.bank)L.push("You're ready. The Overdraft Ogre is hiding in the vault of Coinsworth Bank, in Market Square. Talk to Clara at the counter first. Her switch simulator is great practice!");
    else if(!S.freed.market)L.push("Brilliant work at the Bank! Shrinkflation Sam has the Market next door. He hates good maths.");
    else L.push("You freed Market Square! The Scam Swamp gate opens in the next update.");
    if(S.hp<maxHP())L.push("You look worn out. Let me patch you up. (HP fully restored.)");
    say(L.map(t=>({s:"PENNY",t})),heal);return}
  if(id==="tom"){say([{s:"TOM",t:pick(["Forward scam texts to 7726. It's free, and it helps block the number.","Real government websites always end in .gov.uk.","I check the noticeboard every morning. There's always a Daily Hunt."])}]);return}
  if(id==="leo"){say([{s:"LEO",t:"Psst! Every goblin has a weak spot. Some hate INVESTIGATE, others hate ATTACK. Hit the weak spot for 50% extra damage!"},{s:"LEO",t:"Penny writes down every weak spot you discover. Check the hint when a battle starts."}]);return}
  if(id==="mo"){say([{s:"MO",t:"Welcome to Market Square! Tip from an old trader: multipacks aren't always cheaper. Check the price per item."}]);return}
  if(id==="rosa"){const st=mS("s1");
    if(st.done){say([{s:"ROSA",t:"Thank you again, dear. I froze my card in my banking app just in case. You can do that too, you know!"}]);return}
    if(S.flags.purse){emit("purse");say([{s:"ROSA",t:"My purse! Oh, you're a star."},{s:"ROSA",t:"Lesson learned: if you lose your card, freeze it in your banking app straight away."}]);return}
    if(!st.on){st.on=true;save();say([{s:"ROSA",t:"Oh dear. I dropped my purse somewhere in the long grass on the east side, near the bottom."},{s:"ROSA",t:"Could you look for me? Watch out for those goblins!"}],()=>toast("SIDE QUEST: ROSA'S LOST PURSE"));return}
    say([{s:"ROSA",t:"Any luck? I'm sure it was in the long grass on the east side, near the bottom."}]);return}
  if(id==="dee"){weeklyDrop();return}
  if(id==="clara"){say([{s:"CLARA",t:`Welcome to Coinsworth Bank, ${n}! Want to try our switch simulator? It's a practice run with a made-up offer: no real account, no real money.`,choices:[{label:"START",fn:switchSim},{label:"NOT NOW"}]}]);return}
  if(id==="ben"){say([{s:"BEN",t:"The Overdraft Ogre has locked himself in our vault with everyone's fees!"},{s:"BEN",t:mS("m2").done?"The vault is at the back. Good luck, and read every bit of small print!":"Penny says you need to beat two goblins on Route 1 before facing him."}]);return}
  if(id==="ivy"){say([{s:"IVY",t:"Top tip: when I switch banks I set my Direct Debits up early. “Active” usually means at least one payment has actually gone out!"}]);return}
}
function enterBuilding(id){
  if(id==="home"){say([{s:"",t:"Your home. What would you like to do?",choices:[{label:"REST",fn:()=>{heal();toast("HP RESTORED · GAME SAVED")}},{label:"CHANGE LOOK",fn:()=>creator(false)},{label:"LEAVE"}]}]);return}
  if(id==="lab"){say(["Penny's lab is full of old coupons, piggy banks and a very large calculator. Penny is outside."]);return}
  if(id==="mart"){openShop();return}
  if(id==="exchange"){say(["CLOSED. Rumour says the Hype Wolf is hiding inside... Coming soon!"]);return}
  if(id==="bank"){const st=mS("s2");if(!st.on&&!st.done){st.on=true;setTimeout(()=>toast("SIDE QUEST: SWITCH TRAINING"),700)}goTo("bank",5,8,0);return}
  if(id==="market"){
    if(!S.freed.bank){say([{s:"???",t:"Heh heh. My Market stays shut until that Ogre in the Bank is beaten!"},{s:"",t:"(The Market unlocks after you free the Bank: beat 2 goblins on Route 1, then the Overdraft Ogre in the Bank vault.)"}]);return}
    if(S.freed.market){say([{s:"",t:"The Market is free! Rematch Shrinkflation Sam?",choices:[{label:"FIGHT",fn:()=>bossFight("market")},{label:"LEAVE"}]}]);return}
    bossFight("market");return}
}
function vault(){
  if(!mS("m2").done){say([{s:"???",t:"COME BACK WHEN YOU'RE STRONGER, LITTLE HUNTER!"},{s:"",t:"(The vault is locked. Beat 2 Scam Goblins on Route 1 first.)"}]);return}
  if(S.freed.bank){say([{s:"",t:"The vault is open and the fees are back with their owners. Rematch the Ogre for practice?",choices:[{label:"FIGHT",fn:()=>bossFight("bank")},{label:"LEAVE"}]}]);return}
  bossFight("bank");
}
function bossFight(id){const b=BOSSES[id];startBattle("boss",{...b,id,hp:b.hp,max:b.hp})}

function switchSim(){
  const SIM=[
   {k:"q",fail:"You did a partial switch. The offer needs a full CASS switch.",q:"Clara: “Our offer needs a switch through CASS.” Which kind of switch do you choose?",o:["A full switch: everything moves and the old account closes","A partial switch: copy a few payments and keep the old account open"],a:0,e:"Switch bonuses almost always need a full CASS switch. A partial switch usually won't qualify."},
   {k:"q",q:"Eligibility: you had a Coinsworth Bank account 3 years ago. The terms exclude anyone who's had one in the last 24 months. Can you still get the bonus?",o:["Yes, 3 years is outside the 24-month window","No, any past account rules you out"],a:0,e:"Read the exact window. 3 years ago is outside a 24-month exclusion, so you're eligible."},
   {k:"q",q:"You start the switch on a Monday. CASS takes 7 working days (no weekends). When does it complete?",o:["Friday the same week","Monday the following week","Wednesday the following week"],a:2,e:"Tuesday to Friday is 4 working days, then Monday, Tuesday, Wednesday makes 7. It completes on Wednesday the following week."},
   {k:"pick",fail:"You didn't have 2 active Direct Debits.",q:"The offer needs 2 active Direct Debits. Tap the payments that are Direct Debits.",items:[["Phone bill: Direct Debit, collected monthly",1],["Rent: standing order you send yourself",0],["Gym membership: Direct Debit, collected monthly",1],["Coffee paid on your card",0]],e:"Standing orders and card payments don't count. Only Direct Debits do, and they need to have collected at least one payment."},
   {k:"q",fail:"Your pay-in didn't count: it wasn't £1,000 from an external account within 30 days.",q:"Pay-in rule: “Pay in £1,000 from an external account within 30 days.” Which of these counts?",o:["Transfer £1,000 in from your account at another bank","Move £1,000 between two Coinsworth Bank accounts","Pay in £200 a month for five months"],a:0,e:"It must come from another bank, and it must all arrive within the 30 days."},
   {k:"clause",fail:"You closed the account after 2 months, so the bonus was clawed back.",q:"Before you sign, read the small print. Tap the sentence that could cost you the bonus later.",parts:[["Bonus paid within 28 days of meeting all conditions. ",0],["Offer open to UK residents aged 18+. ",0],["We may reclaim the bonus if you close the account within 6 months. ",1],["Interest rates may change.",0]],e:"That's a clawback clause. Keep the account open for at least 6 months, or you could lose the bonus."}
  ];
  let i=-1,score=0;const fails=[];
  const head=()=>`<h2>COINSWORTH BANK · SWITCH SIMULATOR</h2><p class="steps">STEP ${i+1} OF ${SIM.length}</p>`;
  function intro(){
    modal(`<h2>COINSWORTH BANK · SWITCH SIMULATOR</h2>
      <div class="poster"><strong>SWITCH TO COINSWORTH BANK AND GET £150*</strong><ul><li>Full switch using CASS within 30 days</li><li>Pay in £1,000 from an external account</li><li>2 active Direct Debits</li><li>No Coinsworth Bank account in the last 24 months</li></ul><p class="small">*Full terms apply. Read them carefully...</p></div>
      <p class="demo">Training simulation with a made-up bank and offer. No real account is opened and no real money moves.</p>
      <div class="row"><button class="ghost" id="sx">NOT NOW</button><button class="go" id="sgo">START</button></div>`);
    on("sx",closeModal);on("sgo",()=>{SFX.tap();next()});
  }
  function next(){i++;if(i>=SIM.length){wait();return}const s=SIM[i];s.k==="q"?stepQ(s):s.k==="pick"?stepPick(s):stepClause(s)}
  function feedback(ok,s){
    if(ok){score++;SFX.coin()}else{SFX.hurt();if(s.fail)fails.push(s.fail)}
    $("sfb").innerHTML=`<p class="btext" style="font-size:17px">${ok?'<b class="ok">Correct!</b>':'<b class="bad">Not quite.</b>'}</p><p class="explain">${s.e}</p><button class="go wide" id="snext">${i<SIM.length-1?"NEXT STEP":"FINISH THE SWITCH"}</button>`;
    on("snext",()=>{SFX.tap();next()});$("snext").focus();
  }
  function stepQ(s){
    modal(`${head()}<p class="q">${s.q}</p><div class="opts">${s.o.map((o,k)=>`<button data-k="${k}">${o}</button>`).join("")}</div><div id="sfb"></div>`);
    $("box").querySelectorAll(".opts button").forEach(b=>b.onclick=()=>{const k=+b.dataset.k;$("box").querySelectorAll(".opts button").forEach((x,j)=>{x.disabled=true;if(j===s.a)x.classList.add("right");else if(j===k)x.classList.add("wrong")});feedback(k===s.a,s)});
  }
  function stepPick(s){
    const sel=new Set();
    modal(`${head()}<p class="q">${s.q}</p><div class="opts">${s.items.map((it,k)=>`<button data-k="${k}">${it[0]}</button>`).join("")}</div><button class="go" id="sck">CHECK</button><div id="sfb"></div>`);
    $("box").querySelectorAll(".opts button").forEach(b=>b.onclick=()=>{const k=+b.dataset.k;sel.has(k)?sel.delete(k):sel.add(k);b.classList.toggle("sel");SFX.tap()});
    on("sck",()=>{const ok=s.items.every((it,k)=>!!it[1]===sel.has(k));$("box").querySelectorAll(".opts button").forEach((x,k)=>{x.disabled=true;x.classList.remove("sel");if(s.items[k][1])x.classList.add("right");else if(sel.has(k))x.classList.add("wrong")});$("sck").remove();feedback(ok,s)});
  }
  function stepClause(s){
    let chosen=-1;
    modal(`${head()}<p class="q">${s.q}</p><div class="msg">${s.parts.map((p,k)=>`<button class="seg" data-k="${k}">${p[0]}</button>`).join("")}</div><button class="go" id="sck" disabled>CHECK</button><div id="sfb"></div>`);
    $("box").querySelectorAll(".seg").forEach(b=>b.onclick=()=>{chosen=+b.dataset.k;$("box").querySelectorAll(".seg").forEach(x=>x.classList.toggle("on",x===b));$("sck").disabled=false;SFX.tap()});
    on("sck",()=>{const ok=!!s.parts[chosen][1];$("box").querySelectorAll(".seg").forEach((x,k)=>{x.disabled=true;x.classList.remove("on");if(s.parts[k][1])x.classList.add(ok?"found":"missed");else if(k===chosen)x.classList.add("wrongtap")});$("sck").remove();feedback(ok,s)});
  }
  function wait(){
    const lines=["Day 1: switch started. CASS gets to work.","Day 3: Direct Debits moving across...","Day 7 (working): switch complete. Old account closed, payments redirected.",fails.length?"Day 30: the bank checks the conditions...":"Day 30: all conditions met ✓","Day 51: bonus decision..."];
    modal(`<h2>WAITING FOR THE BONUS...</h2><ul class="timeline" id="tl"></ul><div id="res"></div>`);
    let k=0;const tick=()=>{if(k<lines.length){$("tl").insertAdjacentHTML("beforeend",`<li style="animation-delay:0s">${lines[k++]}</li>`);SFX.tap();setTimeout(tick,550)}else result()};tick();
  }
  function result(){
    const paid=!fails.length,first=!S.flags.simDone;let rw="";
    if(paid&&first){S.flags.simDone=true;S.cards.switchpro=1;rw=reward({coins:40,xp:60})}else rw=reward({xp:paid?15:10});
    const s2=mS("s2");if(!s2.done)s2.on=true;emit("sim");save();if(paid)SFX.win();else SFX.hurt();
    $("res").innerHTML=`<p class="btext">${paid?'<b class="ok">£150 BONUS PAID!</b> (pretend money, real skills)':'<b class="bad">BONUS REFUSED</b>'}</p>
      ${paid?"":`<ul class="flags">${fails.map(f=>`<li>✘ ${f}</li>`).join("")}</ul>`}
      <p class="small">You scored ${score}/${SIM.length}. ${rw}</p>
      ${paid&&first?`<div class="drops">${cardHTML("switchpro",true,true)}</div>`:""}
      ${S.age===true?`<a class="cta" href="${guideURL("pb-bank-switch-bonuses")}" target="_blank" rel="noopener">WANT TO DO IT FOR REAL? SEE LIVE SWITCH OFFERS ↗</a><p class="small">Money Hunters may earn a referral fee from some offers, at no cost to you. The game never rewards you for signing up.</p>`:`<a class="learn" href="${guideURL("pb-bank-switch-bonuses")}" target="_blank" rel="noopener">Read the full bank switch guide ↗</a>`}
      <div class="row"><button class="ghost" id="sag">TRY AGAIN</button><button class="go" id="sdone">DONE</button></div>`;
    on("sdone",closeModal);on("sag",()=>{i=-1;score=0;fails.length=0;intro()});
  }
  intro();
}

function drawWorld(t){
  const pk=P.moving?P.mt:1,ppx=P.fx+(P.x-P.fx)*pk,ppy=P.fy+(P.y-P.fy)*pk,W=MAP.w*TS,H=MAP.h*TS;
  const camx=W<240?-Math.round((240-W)/2):Math.round(Math.max(0,Math.min(W-240,ppx*TS+8-120)));
  const camy=H<208?-Math.round((208-H)/2):Math.round(Math.max(0,Math.min(H-208,ppy*TS+8-104)));
  R(0,0,240,208,"#0b0d1a");
  const x0=Math.max(0,Math.floor(camx/TS)),y0=Math.max(0,Math.floor(camy/TS));
  for(let y=y0;y<=y0+VH&&y<MAP.h;y++)for(let x=x0;x<=x0+VW&&x<MAP.w;x++)drawTile(x,y,x*TS-camx,y*TS-camy,t);
  MAP.blds.forEach(b=>drawBuilding(b,camx,camy,t));
  const objs=[];
  MAP.npcs.forEach(n=>objs.push({k:"npc",n,x:n.x,y:n.y}));MAP.signs.forEach(s=>objs.push({k:"sign",x:s.x,y:s.y}));
  if(MAP.board)objs.push({k:"board",x:MAP.board.x,y:MAP.board.y});if(MAP.cart)objs.push({k:"cart",x:MAP.cart.x,y:MAP.cart.y});
  MAP.chests.forEach(ch=>objs.push({k:"chest",ch,x:ch.x,y:ch.y}));
  if(MAP.id==="town"){const d=daily(),g=gemSpot(),dist=(x,y)=>Math.abs(x-P.x)+Math.abs(y-P.y);
    if(!d.gem&&(d.read||isCls("scout")))objs.push({k:"spark",x:g[0],y:g[1],col:"#7ae8ff"});
    if(!S.flags.purse&&mS("s1").on&&dist(PURSE.x,PURSE.y)<=(isCls("scout")?6:2))objs.push({k:"spark",x:PURSE.x,y:PURSE.y,col:"#ff9ad8"})}
  objs.push({k:"player",x:ppx,y:ppy});objs.sort((a,b)=>a.y-b.y);
  objs.forEach(o=>{const X=Math.round(o.x*TS-camx),Y=Math.round(o.y*TS-camy);if(X>-16&&Y>-24&&X<256&&Y<224)drawObj(o,X,Y,t)});
  if(MAP.M[P.y][P.x]==='"'&&!P.moving){const X=P.x*TS-camx,Y=P.y*TS-camy;R(X,Y+10,16,6,"#4aa553");for(let k=0;k<4;k++){R(X+1+k*4,Y+9,1,7,"#2c7a38");R(X+2+k*4,Y+8,1,6,"#3a8f45")}}
  rustles=rustles.filter(r=>{r.t+=16;const X=r.x*TS-camx,Y=r.y*TS-camy,k=r.t/300;for(let i=0;i<4;i++)R(Math.round(X+8+Math.cos(i*1.6)*k*10),Math.round(Y+8-k*8+i),2,2,"#2c7a38");return r.t<300});
}
