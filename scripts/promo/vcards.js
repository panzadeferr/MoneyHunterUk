const {chromium}=require('playwright');const fs=require('fs');
const F=__dirname+'/fonts/node_modules/@fontsource';const b64=f=>'data:font/woff2;base64,'+fs.readFileSync(f).toString('base64');
const img=k=>'data:image/png;base64,'+fs.readFileSync(__dirname+'/spr_'+k+'.png').toString('base64');
const V=[
['pete','PICKPOCKET PETE',5,2,'Sticky Fingers','£2.99 here, £4.99 there, every month, forever','People who actually read their statement','"Nice shop. Shame about all those little fees nobody checks."'],
['captain','CAPTAIN OVERDRAFT',7,3,'Fee Storm','Keeps you in the red so his sails stay full','The small print','"Stay in the red, sailor! Every pound you owe fills my sails."'],
['twins','THE SHRINK-RAY TWINS',9,2,'Shrink Ray','Same price, smaller pack, straight face','Price per kilo','"Same price! Smaller pack! Nobody ever notices, do they?"'],
['carl','CONTRACT CARL',11,3,'The 40-Page Contract','Turns "only £15 a month" into 24 months','"I\'ll think about it"','"Sign here. And here. Oh, and the next 24 months of your life."'],
['taxman','THE FAKE TAXMAN',13,4,'Final Notice Panic','Demands payment in gift cards within the hour','Calling HMRC on the number from gov.uk','"Pay in gift cards within the hour or we send the bailiffs!"'],
['phisher','THE PHISHERMAN',15,5,'Mega Net','"Your parcel could not be delivered"','Not clicking the link','"Just a little click... and you\'re hooked."'],
['grimsby','MR GRIMSBY',17,5,'Ledger of Debts','Very polite. Takes everything you own.','Paying in full, on time','"I will remain very polite while I take everything you own."']];
const css=`@font-face{font-family:P;src:url(${b64(F+'/press-start-2p/files/press-start-2p-latin-400-normal.woff2')})}
@font-face{font-family:X;font-weight:700;src:url(${b64(F+'/pixelify-sans/files/pixelify-sans-latin-700-normal.woff2')})}
@font-face{font-family:X;font-weight:400;src:url(${b64(F+'/pixelify-sans/files/pixelify-sans-latin-400-normal.woff2')})}
*{box-sizing:border-box}body{margin:0;background:#161a33}
.w{width:1080px;height:1350px;padding:60px 90px;background:#161a33;font-family:X;color:#161a33}
.top{font-family:P;color:#ffc94a;font-size:26px;text-align:center;margin-bottom:26px;letter-spacing:2px}
.card{background:#ffc94a;border:10px solid #f3f0ff;border-radius:34px;padding:26px;box-shadow:0 0 0 8px #e0a92e,0 24px 0 8px rgba(0,0,0,.35)}
.hd{display:flex;justify-content:space-between;align-items:center;font-family:P;font-size:30px;padding:6px 8px 18px}
.hd span{font-size:24px;background:#161a33;color:#ffc94a;padding:10px 12px}
.art{height:470px;border:8px solid #161a33;border-radius:12px;background-size:cover;background-position:center;image-rendering:pixelated}
.row{display:flex;gap:16px;margin-top:20px}
.box{background:#fff8e0;border:5px solid #161a33;border-radius:10px;padding:14px 18px;font-size:30px;line-height:1.2;flex:1}
.box b{display:block;font-family:P;font-size:15px;color:#d6283c;margin-bottom:8px}
.q{margin-top:16px;font-size:32px;font-style:italic;line-height:1.25;padding:6px 10px}
.danger{font-family:P;font-size:18px;margin-top:6px;padding:0 10px}
.ft{display:flex;justify-content:space-between;color:#a7aad4;font-size:30px;margin-top:34px}.ft b{font-family:P;font-size:20px;color:#ffc94a}`;
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1350}});let i=0;
for(const [k,name,lv,d,move,desc,weak,quote] of V){i++;
 await p.setContent(`<style>${css}</style><div class="w"><div class="top">MONEY VILLAIN ${i}/7</div><div class="card"><div class="hd">${name}<span>LV ${lv}</span></div>
 <div class="art" style="background-image:url(${img(k)})"></div>
 <div class="row"><div class="box"><b>SPECIAL MOVE</b>${move}: ${desc}</div></div>
 <div class="row"><div class="box"><b>WEAKNESS</b>${weak}</div></div>
 <div class="q">${quote}</div><div class="danger">DANGER ${'■'.repeat(d)}${'□'.repeat(5-d)}</div></div>
 <div class="ft"><span>Beat him free: moneyhunters.co.uk/play</span><b>#COINSWORTH</b></div></div>`);
 await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(80);
 const h=await p.evaluate(()=>document.querySelector('.w').scrollHeight);if(h>1350)console.log('OVER',k,h);
 await p.screenshot({path:`out/villains/villain${i}_${k}.png`});}
await br.close()})();
