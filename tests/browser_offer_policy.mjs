// Runs tests/offer_policy_cases.json against the app's JavaScript copy of the rules, then checks the rendered app.
// Needs a local server on :8765 and Playwright: PLAYWRIGHT=/path/index.mjs CHROMIUM=/path/chromium node tests/browser_offer_policy.mjs
import fs from 'fs';
const {chromium} = await import(process.env.PLAYWRIGHT || 'playwright');
const cases = JSON.parse(fs.readFileSync(new URL('./offer_policy_cases.json', import.meta.url)));
const b = await chromium.launch(process.env.CHROMIUM ? {executablePath: process.env.CHROMIUM} : {});
const p = await b.newPage({viewport: {width: 420, height: 900}});
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.route(u => !u.hostname.includes('localhost'), r => r.abort());
await p.addInitScript(() => { localStorage.setItem('mh_onboarded_v2', '1'); const q = {select: () => q, eq: () => q, order: () => q, limit: () => q, single: () => q, then: r => r({data: [], error: null})}; window.supabase = {createClient: () => ({auth: {getSession: async () => ({data: {session: null}}), onAuthStateChange: () => ({data: {subscription: {unsubscribe() {}}}}), getUser: async () => ({data: {user: null}})}, from: () => q, channel: () => ({on: () => ({subscribe() {}}), subscribe() {}}), rpc: async () => ({data: null})}) }; });
await p.goto('http://localhost:8765/app.html'); await p.waitForTimeout(3000);
const out = []; const ok = (n, c, x = '') => out.push((c ? 'PASS ' : 'FAIL ') + n + (x ? ' — ' + x : ''));
for (const c of cases.display_amount) {
  const got = await p.evaluate(({c}) => { const o = {id: 'zz', name: 'Zzprov', reward: c.raw, amount: 1, desc: c.text}; const save = JSON.stringify(OFFER_STATE); OFFER_STATE = {zzprov: c.state}; applyOfferPolicy(o); OFFER_STATE = JSON.parse(save); return o.reward; }, {c});
  ok('display_amount: ' + c.name, got === c.expect, got);
}
for (const [a, e] of cases.plain) { const got = await p.evaluate(a => plainWording(a), a); ok('plain: ' + a, got === e, got); }
for (const c of cases.verification_label) { const got = await p.evaluate(({c}) => { const save = JSON.stringify(OFFER_STATE); OFFER_STATE = {zzprov: c.state}; const r = offerVerLabel({name: 'Zzprov'}); OFFER_STATE = JSON.parse(save); return r; }, {c}); ok('verification: ' + c.name, got === c.expect, got); }
// rendered app
const st = await p.evaluate(() => Object.keys(OFFER_STATE).length); ok('app loaded offer_state.json', st > 50, String(st));
const bad = await p.evaluate(() => offers.filter(o => offerIsInvesting(o) && (/£\s?\d/.test(o.reward) && !/^up to/.test(o.reward))).map(o => o.id)); ok('investing offers show no £ in the reward', bad.length === 0, bad.join(','));
const hidden = await p.evaluate(() => offers.filter(o => /etoro|xtb|trading ?212/i.test(o.id + o.name)).map(o => o.id)); ok('CFD brokers absent', hidden.length === 0, hidden.join(','));
const ig = await p.evaluate(() => offers.find(o => o.id === 'ig-trading')); ok('IG live as Share dealing account', !!ig && /Share dealing account/.test(ig.name) && ig.reward === 'Sign-up reward, value varies', ig && ig.reward);
const freeBad = await p.evaluate(() => offers.filter(o => /\bfree\b/i.test([o.name, o.reward, o.desc, o.action].join(' '))).map(o => o.id)); ok('no "free" in offer text', freeBad.length === 0, freeBad.join(','));
const panel = await p.evaluate(() => { openPanel(offers.find(o => o.id === 'freetrade')); const f = document.getElementById('panelFooter'); const r = f.querySelector('.panel-risk'), btn = f.querySelector('.panel-claim'); return {risk: !!r, order: r && btn ? !!(r.compareDocumentPosition(btn) & Node.DOCUMENT_POSITION_FOLLOWING) : false, body: document.getElementById('panelBody').innerText}; });
ok('panel: risk warning directly above the claim button', panel.risk && panel.order);
ok('panel: Ad notice present and verification label', /Ad/.test(panel.body) && /not verified by a person/.test(panel.body));
const prem = await p.evaluate(() => offers.filter(o => /premier/i.test(o.name)).map(o => [o.id, o.reward, !!offerState(o).conditions])); ok('Premier amounts only with conditions', prem.every(([i, r, c]) => c || !/£/.test(r)), JSON.stringify(prem));
ok('no page errors', errs.length === 0, errs.join(';'));
console.log(out.join('\n')); await b.close();
