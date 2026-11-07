// usage: node cap.js spec.json  -> renders each {name, html} into name.png 1080x1920 transparent
const {chromium}=require('playwright');const fs=require('fs');
const F=__dirname+'/fonts/node_modules/@fontsource';
const b64=f=>'data:font/woff2;base64,'+fs.readFileSync(f).toString('base64');
const css=`@font-face{font-family:P;src:url(${b64(F+'/press-start-2p/files/press-start-2p-latin-400-normal.woff2')})}@font-face{font-family:X;font-weight:700;src:url(${b64(F+'/pixelify-sans/files/pixelify-sans-latin-700-normal.woff2')})}
body{margin:0;width:1080px;height:1920px;background:transparent;position:relative;font-family:X,sans-serif}
.hook{position:absolute;left:60px;right:60px;top:230px;background:#fff;color:#161a33;border:8px solid #161a33;box-shadow:0 0 0 6px #ffc94a,0 18px 0 6px rgba(0,0,0,.35);padding:34px 36px;font-size:66px;line-height:1.12;text-align:center;font-weight:700}
.hook b{color:#d6283c}.hook i{font-style:normal;background:#ffc94a;padding:0 10px}
.mid{position:absolute;left:90px;right:90px;top:250px;background:#161a33ee;color:#fff;border:6px solid #ffc94a;padding:24px 28px;font-size:52px;line-height:1.15;text-align:center}
.mid b{color:#ffc94a}
.end{position:absolute;inset:0;background:rgba(14,16,36,.93);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:#fff;padding:0 70px}
.end .t{font-family:P;color:#ffc94a;font-size:58px;line-height:1.35;margin-bottom:40px}
.end .s{font-size:60px;line-height:1.2;margin-bottom:56px}
.end .u{font-family:P;font-size:34px;background:#ffc94a;color:#161a33;padding:26px 30px;border-bottom:10px solid #b8861a}
.end .f{font-size:44px;color:#a7aad4;margin-top:44px}`;
(async()=>{const spec=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const c of spec){await p.setContent(`<style>${css}</style>${c.html}`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(100);await p.screenshot({path:c.name,omitBackground:true});}
await b.close()})();
