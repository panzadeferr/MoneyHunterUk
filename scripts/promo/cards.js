const {chromium}=require('playwright');const fs=require('fs');
const F=__dirname+'/fonts/node_modules/@fontsource';const b64=f=>'data:font/woff2;base64,'+fs.readFileSync(f).toString('base64');
const hero='data:image/png;base64,'+fs.readFileSync(__dirname+'/hero.png').toString('base64');
const css=`@font-face{font-family:P;src:url(${b64(F+'/press-start-2p/files/press-start-2p-latin-400-normal.woff2')})}
@font-face{font-family:X;font-weight:400;src:url(${b64(F+'/pixelify-sans/files/pixelify-sans-latin-400-normal.woff2')})}
@font-face{font-family:X;font-weight:700;src:url(${b64(F+'/pixelify-sans/files/pixelify-sans-latin-700-normal.woff2')})}
*{box-sizing:border-box}body{margin:0}
.s{width:1080px;height:1350px;background:#161a33;color:#f3f0ff;font-family:X;position:relative;padding:80px 70px;overflow:hidden}
.s:before{content:"";position:absolute;inset:0;background-image:linear-gradient(#20254a 3px,transparent 3px),linear-gradient(90deg,#20254a 3px,transparent 3px);background-size:60px 60px;opacity:.7}
.s>*{position:relative}
.tag{display:inline-block;font-family:P;font-size:26px;background:#ff6470;color:#fff;padding:14px 18px;border-bottom:8px solid #b23a44}
.tag.y{background:#ffc94a;color:#161a33;border-color:#b8861a}.tag.g{background:#5fd38d;color:#161a33;border-color:#2f8a55}
h1{font-family:P;font-size:46px;line-height:1.35;color:#ffc94a;margin:40px 0 30px}
.src{font-size:34px;color:#a7aad4;margin-bottom:22px}
.msg{background:#f6f1e3;color:#1b1f3a;border:8px solid #3c4382;border-radius:0 30px 30px 30px;padding:40px 44px;font-size:44px;line-height:1.38}
.msg .fl{background:#ffd6da;color:#b3122a;border-bottom:5px solid #ff6470}
.msg sup{font-family:P;font-size:20px;background:#ff6470;color:#fff;padding:4px 7px;margin-left:4px;vertical-align:6px}
ol{margin:36px 0 0;padding:0;list-style:none;font-size:36px;line-height:1.3}
ol li{display:flex;gap:20px;margin-bottom:22px}ol li b{font-family:P;font-size:22px;background:#ff6470;color:#fff;min-width:46px;height:46px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.foot{position:absolute;left:70px;right:70px;bottom:60px;display:flex;justify-content:space-between;align-items:center;font-size:32px;color:#a7aad4}
.foot .b{font-family:P;font-size:22px;color:#ffc94a}
.big{font-size:64px;line-height:1.2;font-weight:700;margin:50px 0}
.big em{font-style:normal;color:#ffc94a}
.ex{font-size:40px;line-height:1.35;color:#d9daf2}
.cta{margin-top:50px;display:flex;gap:40px;align-items:center}
.cta img{width:230px;height:230px;image-rendering:pixelated;background:#ffc94a;border-radius:50%;padding:20px}
.u{display:inline-block;font-family:P;font-size:28px;background:#ffc94a;color:#161a33;padding:20px 24px;border-bottom:8px solid #b8861a;margin-top:22px}
`;
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const foot=(n,t)=>`<div class="foot"><span>${t}</span><span class="b">#COINSWORTH</span></div>`;
(async()=>{const d=JSON.parse(fs.readFileSync(__dirname+'/cdata.json','utf8'));const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1350}});
async function shot(html,path){await p.setContent(`<style>${css}</style><div class="s">${html}</div>`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(80);
 const over=await p.evaluate(()=>{const s=document.querySelector('.s');return [...s.children].some(c=>!c.classList.contains('foot')&&c.getBoundingClientRect().bottom>1350-130)});
 if(over)console.log('OVERFLOW',path);await p.screenshot({path});}
let n=0;for(const q of d.inv){n++;const id=String(n).padStart(2,'0');const src=q.src.replace(/[“”]/g,'"');
 const flags=q.parts.filter(x=>x.f).length;
 const plain=q.parts.map(x=>esc(x.s)).join('');
 await shot(`<span class="tag">SPOT THE SCAM #${n}</span><h1>How many red flags can you find?</h1><div class="src">${esc(src)}</div><div class="msg">${plain}</div>${foot(n,'Swipe for the answer &rarr;')}`,`out/scams/scam${id}_1.png`);
 let k=0;const marked=q.parts.map(x=>x.f?`<span class="fl">${esc(x.s.trim()?x.s:'')}</span><sup>${++k}</sup>`:esc(x.s)).join('');k=0;
 const list=q.parts.filter(x=>x.f).map(x=>`<li><b>${++k}</b><span>${esc(x.w)}</span></li>`).join('');
 await shot(`<span class="tag">${flags} RED FLAGS</span><div class="msg" style="margin-top:40px">${marked}</div><ol>${list}</ol>${foot(n,'Swipe &rarr;')}`,`out/scams/scam${id}_2.png`);
 await shot(`<span class="tag g">THE GOLDEN RULE</span><div class="big">${esc(q.e)}</div><div class="cta"><img src="${hero}"><div><div class="ex">Catch 40 real UK scams like this one in my free retro game <b style="color:#ffc94a">Coinsworth</b>.</div><span class="u">moneyhunters.co.uk/play</span></div></div>${foot(n,'Save this for later')}`,`out/scams/scam${id}_3.png`);
}
const facts=[
 ['Overdraft fees changed in 2020','UK overdrafts no longer charge <em>daily or monthly fees</em>. Since 2020 they use one annual interest rate.','FCA rules banned the old fixed fees. Compare the rate, often around 35-40%, before you use one.'],
 ['Joint accounts are covered twice','A joint account is protected up to <em>£120,000 per person</em> by the FSCS.','That is £240,000 for a couple, per banking licence. Check which brands share a licence.'],
 ['Changed your mind online?','For most online buys from a UK trader you have <em>14 days</em> to cancel.','Some items are excluded, like personalised goods. Keep the order email.'],
 ['A free credit score boost','Being on the <em>electoral roll</em> can help your credit score.','Lenders use it to confirm your identity and address. Register on gov.uk.'],
 ['Opting out costs you','Leave your workplace pension and you lose your <em>employer\'s contributions</em>.','That is free money from your employer, on top of your own pay.'],
 ['Married? Check this','Marriage Allowance lets one partner pass <em>£1,260</em> of tax-free allowance to the other.','Up to £252 a year off your tax bill, and it can be backdated 4 years. Apply free on gov.uk.']];
let m=0;for(const [t,big,ex] of facts){m++;await shot(`<span class="tag y">MONEY FACT</span><h1>${t}</h1><div class="big" style="font-size:60px">${big}</div><div class="ex">${ex}</div><div class="cta" style="margin-top:60px"><img src="${hero}" style="width:180px;height:180px"><div class="ex" style="font-size:34px">Learn this and 367 more in my free retro money game.<br><span class="u" style="font-size:24px">moneyhunters.co.uk/play</span></div></div>${foot(m,'Not financial advice')}`,`out/facts/fact${String(m).padStart(2,'0')}.png`);}
await br.close()})();
