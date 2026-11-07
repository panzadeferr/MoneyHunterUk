const {chromium}=require('playwright');const fs=require('fs');
const F=__dirname+'/fonts/node_modules/@fontsource';const b64=f=>'data:font/woff2;base64,'+fs.readFileSync(f).toString('base64');
const IF=__dirname+'/fonts/node_modules/@fontsource/inter/files/';
const css=`@font-face{font-family:P;src:url(${b64(F+'/press-start-2p/files/press-start-2p-latin-400-normal.woff2')})}
@font-face{font-family:I;font-weight:400;src:url(${b64(IF+'inter-latin-400-normal.woff2')})}@font-face{font-family:I;font-weight:800;src:url(${b64(IF+'inter-latin-800-normal.woff2')})}
*{box-sizing:border-box}body{margin:0}.s{width:1080px;height:1350px;background:#0b0f14;color:#f3f4f6;font-family:I;padding:80px 76px;position:relative}
.tag{display:inline-block;font-family:P;font-size:24px;background:#22e27e;color:#0b0f14;padding:14px 18px}
.bank{font-size:56px;font-weight:800;margin:50px 0 10px}.amt{font-size:190px;font-weight:800;color:#22e27e;line-height:1}
.plus{font-size:44px;color:#ffc94a;font-weight:800;margin-top:20px;line-height:1.3}
.box{margin-top:46px;border:3px solid #1f2933;border-radius:28px;padding:34px 38px;font-size:36px;line-height:1.45;background:#111820}
.box b{color:#ffc94a}
ul{margin:20px 0 0;padding-left:0;list-style:none;font-size:38px;line-height:1.45}ul li{padding-left:56px;position:relative;margin-bottom:14px}ul li:before{content:"✓";position:absolute;left:0;color:#22e27e;font-weight:800}
.warn{margin-top:30px;font-size:30px;color:#9ca3af;line-height:1.4}
.foot{position:absolute;left:76px;right:76px;bottom:60px;display:flex;justify-content:space-between;font-size:28px;color:#9ca3af}.foot b{font-family:P;font-size:20px;color:#22e27e}
h2{font-size:54px;font-weight:800;margin:44px 0 10px}`;
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1350}});
const shot=async(h,f)=>{await p.setContent(`<style>${css}</style><div class="s">${h}</div>`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(80);await p.screenshot({path:f})};
await shot(`<span class="tag">BANK SWITCH OF THE WEEK</span><div class="bank">first direct</div><div class="amt">£175</div><div class="plus">+ £35 extra if you open by 2 Dec<br>+ up to £25 via TopCashback</div>
<div class="box">Up to <b>£235</b> in total for switching your current account. Conditions on the next slide.</div>${foot('Swipe for the conditions →')}`,'out/app/switch_week_1.png');
await shot(`<span class="tag">THE CONDITIONS</span><h2>Do all of this within 45 days</h2><ul><li>Full switch using CASS, closing your old account</li><li>Move at least 2 direct debits or standing orders</li><li>Pay in £1,000</li><li>Make 5 debit card payments</li><li>Log on to the app or online banking</li></ul>
<div class="warn">New customers only: not if you've had a first direct product, or opened an HSBC current account since 1 Jan 2018. TopCashback: click through before you apply. Cashback can take weeks or months to pay. Offers change; check the bank's terms first. Not financial advice.</div>${foot('All live switch offers: moneyhunters.co.uk')}`,'out/app/switch_week_2.png');
await br.close()})();
function foot(t){return `<div class="foot"><span>${t}</span><b>MONEY HUNTERS UK</b></div>`}
