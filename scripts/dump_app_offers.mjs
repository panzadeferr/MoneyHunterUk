// Dumps the offers array the app actually renders (curated + scraped merge) to JSON, for the offer register.
// Usage: PLAYWRIGHT=/path/to/playwright/index.mjs CHROMIUM=/path/to/chromium node scripts/dump_app_offers.mjs out.json
// Needs a local server on :8765 (python3 -m http.server 8765). External requests are blocked and supabase is stubbed.
import fs from 'fs';
const {chromium} = await import(process.env.PLAYWRIGHT || 'playwright');
const b = await chromium.launch(process.env.CHROMIUM ? {executablePath: process.env.CHROMIUM} : {});
const p = await b.newPage({viewport: {width: 420, height: 900}});
await p.route(u => !u.hostname.includes('localhost'), r => r.abort());
await p.addInitScript(() => {
  localStorage.setItem('mh_onboarded_v2', '1');
  const q = {select: () => q, eq: () => q, order: () => q, limit: () => q, single: () => q, then: r => r({data: [], error: null})};
  window.supabase = {createClient: () => ({auth: {getSession: async () => ({data: {session: null}}), onAuthStateChange: () => ({data: {subscription: {unsubscribe() {}}}}), getUser: async () => ({data: {user: null}})}, from: () => q, channel: () => ({on: () => ({subscribe() {}}), subscribe() {}}), rpc: async () => ({data: null})})};
});
await p.goto('http://localhost:8765/app.html');
await p.waitForTimeout(3500);
const out = await p.evaluate(() => ({
  offers: offers.map(o => ({id: o.id, name: o.name, reward: o.reward, amount: o.amount, url: o.url, desc: o.desc, badge: o.badge, category: o.category || '', verified: o.verified || '', end: (OFFER_REVIEW[o.id] || {}).end || '', ref: offerIsRef(o), noLink: offerNoLink(o), investing: offerIsInvesting(o), orig: o._orig || null, curated: !/-(s|sc|ml)$/.test(o.id)}))
}));
fs.writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
console.log('app offers', out.offers.length);
await b.close();
