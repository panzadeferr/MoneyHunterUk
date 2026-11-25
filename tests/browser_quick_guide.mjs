// Checks the "Offers to look at first" pop-up: one high-value bank switch plus offers that carry the referral link.
// Needs a local server on :8765: PLAYWRIGHT=/path/index.mjs CHROMIUM=/path/chromium node tests/browser_quick_guide.mjs
import fs from 'fs';
const {chromium} = await import(process.env.PLAYWRIGHT || 'playwright');
const b = await chromium.launch(process.env.CHROMIUM ? {executablePath: process.env.CHROMIUM} : {});
const p = await b.newPage({viewport: {width: 420, height: 900}});
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.route(u => !u.hostname.includes('localhost'), r => r.abort());
await p.addInitScript(() => { localStorage.setItem('mh_onboarded_v2', '1'); const q = {select: () => q, eq: () => q, order: () => q, limit: () => q, single: () => q, then: r => r({data: [], error: null})}; window.supabase = {createClient: () => ({auth: {getSession: async () => ({data: {session: null}}), onAuthStateChange: () => ({data: {subscription: {unsubscribe() {}}}}), getUser: async () => ({data: {user: null}})}, from: () => q, channel: () => ({on: () => ({subscribe() {}}), subscribe() {}}), rpc: async () => ({data: null})}) }; });
await p.goto('http://localhost:8765/app.html'); await p.waitForTimeout(3000);
const out = []; const ok = (n, c, x = '') => out.push((c ? 'PASS ' : 'FAIL ') + n + (x ? ' — ' + x : ''));
const r = await p.evaluate(() => {
  showQuickGuide();
  const steps = [...document.querySelectorAll('#quickGuideSteps .quick-guide-step')].map(s => ({
    title: s.querySelector('.quick-guide-step-title').innerText.replace(/\s+/g, ' '),
    desc: s.querySelector('.quick-guide-step-desc').innerText,
    ad: /\bAd\b/.test(s.querySelector('.quick-guide-step-title').innerText)}));
  return {steps, title: document.getElementById('quickGuideTitle').textContent, sub: document.getElementById('quickGuideSub').textContent,
    total: document.getElementById('quickGuideTotal').innerText};
});
ok('shows 3 picks', r.steps.length === 3, JSON.stringify(r.steps.map(s => s.title)));
ok('first pick is a bank switch from the big-bank list', /Barclays|Santander|HSBC|First Direct|Co-operative|Lloyds/i.test(r.steps[0].title), r.steps[0].title);
ok('picks 2 and 3 carry the Ad label', r.steps.slice(1).every(s => s.ad), JSON.stringify(r.steps.slice(1).map(s => s.title)));
ok('no promise of "£300+" in the headline', !/£300/.test(r.title + r.sub), r.title);
ok('headline says referral links are marked Ad', /marked Ad/.test(r.sub), r.sub);
ok('investing picks carry a risk warning', r.steps.filter(s => /Webull|Freetrade/i.test(s.title)).every(s => /Capital at risk/.test(s.desc)));
ok('no forbidden words', !/\bfree money|guaranteed|risk-free/i.test(JSON.stringify(r)));
console.log(out.join('\n')); await b.close(); process.exit(out.some(l => l.startsWith('FAIL')) ? 1 : 0);
