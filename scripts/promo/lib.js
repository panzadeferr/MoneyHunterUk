const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const F='__WORKDIR__/fonts/node_modules/@fontsource';
const fontMap={'ps2p.woff2':F+'/press-start-2p/files/press-start-2p-latin-400-normal.woff2','px400.woff2':F+'/pixelify-sans/files/pixelify-sans-latin-400-normal.woff2','px600.woff2':F+'/pixelify-sans/files/pixelify-sans-latin-600-normal.woff2'};
async function setup(opts={}){
 const b=await chromium.launch();
 const c=await b.newContext({viewport:{width:1080,height:1920},deviceScaleFactor:1,isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'});
 await c.route('**/fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:fs.readFileSync('__WORKDIR__/fonts/local.css','utf8')}));
 await c.route('**/fonts.gstatic.com/l/**',r=>{const f=r.request().url().split('/').pop();r.fulfill({contentType:'font/woff2',body:fs.readFileSync(fontMap[f])})});
 await c.route('**/cloud.umami.is/**',r=>r.abort());
 await c.addInitScript(()=>{const z=()=>{document.documentElement.style.zoom='2.5'};if(document.documentElement)z();document.addEventListener('DOMContentLoaded',z)});
 if(opts.save) await c.addInitScript(s=>{try{localStorage.setItem('mh_coinsworth6',s)}catch(e){}},opts.save);
 const p=await c.newPage();p.on('pageerror',e=>console.log('PAGEERR',e.message));
 await p.goto('http://localhost:8766/play/');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
 return {b,c,p};
}
async function startRec(p,dir){
 fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir,{recursive:true});
 const cdp=await p.context().newCDPSession(p);const frames=[];let first=null;const marks={};
 cdp.on('Page.screencastFrame',async f=>{const n=frames.length;const fn=path.join(dir,String(n).padStart(5,'0')+'.jpg');fs.writeFileSync(fn,Buffer.from(f.data,'base64'));frames.push({fn,t:f.metadata.timestamp});if(first===null)first=Date.now();cdp.send('Page.screencastFrameAck',{sessionId:f.sessionId}).catch(()=>{})});
 await cdp.send('Page.startScreencast',{format:'jpeg',quality:92,maxWidth:1080,maxHeight:1920,everyNthFrame:1});
 const t0=Date.now()/1000;
 return {mark:(n)=>{marks[n]=first===null?0:(Date.now()-first)/1000},stop:async()=>{await p.waitForTimeout(150);await cdp.send('Page.stopScreencast');const end=frames.length?frames[frames.length-1].t+0.04:0;
   let txt='';for(let i=0;i<frames.length;i++){const d=(i+1<frames.length?frames[i+1].t:end)-frames[i].t;txt+=`file '${frames[i].fn}'\nduration ${Math.max(d,0.001).toFixed(4)}\n`}
   if(frames.length)txt+=`file '${frames[frames.length-1].fn}'\n`;fs.writeFileSync(path.join(dir,'list.txt'),txt);fs.writeFileSync(path.join(dir,'marks.json'),JSON.stringify(marks));return {n:frames.length,dur:end-frames[0].t,marks}}};
}
const sleep=(p,ms)=>p.waitForTimeout(ms);
async function hold(p,key,ms){await p.keyboard.down(key);await p.waitForTimeout(ms);await p.keyboard.up(key);}
module.exports={setup,startRec,sleep,hold};
