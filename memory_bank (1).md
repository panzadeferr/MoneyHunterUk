# MoneyHunterUk Memory Bank

## Project Overview
**MoneyHunterUk** is a UK referral deal tracker PWA that helps users find and track bank switches, cashback offers, investment bonuses, and supermarket deals. The mission: help UK users earn £300–£1,000+ in their first 3 months by following step-by-step guides.

### Core Value Proposition
- Track 100+ verified UK deals (bank switches, referrals, cashback, invest bonuses)
- Supermarket gift card stacking (JamDoughnut, Airtime, Everup)
- Step-by-step idiot-proof guides for complete beginners
- XP/gamification system (levels, badges, streaks, missions, raffle)
- Free forever

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Single-file `app.html` PWA (vanilla JS, no framework) |
| Backend | Railway-hosted Telegram bot (`bot.py`) |
| Database | Supabase (`wqcwevcdmiounmoqhqpg.supabase.co`, client always named `db`) |
| Hosting | GitHub Pages |
| Repo | github.com/panzadeferr/MoneyHunterUk |
| Email | Brevo via Railway proxy |

---

## Critical Constants (NEVER change)

```
Supabase URL: wqcwevcdmiounmoqhqpg.supabase.co
Supabase client: always named db
Admin secret: mh_admin_2026
Admin email: hello@moneyhunters.co.uk
localStorage keys: prefixed mh_ — never rename
RAFFLE_ENABLED = false (launches at 25 users)
Stable git tag: v1.0-stable
Restore command: git checkout v1.0-stable -- app.html
```

---

## Architecture

### app.html Structure (CRITICAL)
- Single file, ~7200 lines
- External Supabase script at line ~17
- Main `<script>` opens near line 3820 with `/* OFFERS STORAGE` comment
- **Always split into 3 parts when editing**: `part_before | part_js | part_after`
- Use `raw.rfind('<script>')` and `raw.rfind('</script>')` — never regex on script tags (breaks due to Supabase `</script>` on line 17)
- After reassembly, check for duplicate `</script>` tags
- Always run JS syntax check: `node --check /tmp/check.js` before declaring done

### Key Files
```
app.html          — Main PWA (single file, all JS/CSS embedded)
index.html        — Landing page
all_deals.json    — Scraped deals data
scraper.py        — Data collection script
bot.py            — Railway Telegram bot
manifest.json     — PWA manifest
sw.js             — Service worker
```

---

## Affiliate & Partnerships Status (April 2026)

| Partner | Status |
|---------|--------|
| Awin | Rejected twice — reapply ~June 2026 with traffic data |
| Impact.com | ✅ Approved — meta tag verified |
| CJ Affiliate | Not yet applied |
| Freetrade direct | Not yet applied |
| TopCashback Publisher | Not yet applied |
| Tillo B2B API | Awaiting reply (onboarding@tillo.io) |
| JamDoughnut B2B | Awaiting reply |

---

## Alberto's Referral Links (used in app — never change)

### Cashback/Rewards
- TopCashback: topcashback.co.uk/ref/Panzadeferr
- Quidco: quidco.onelink.me/nKzg/v2f3f7m0
- Rakuten: rakuten.co.uk/r/ALBERT24541
- JamDoughnut code: **8TGF** (always featured first)
- Airtime code: FRJKFXX3
- Curve: curve.com/join#NQ77G4WE
- Zilch: zilch.onelink.me/x8EV/zdehyy8s
- Everup: everup.onelink.me/9lgD/3d22pmln
- Cheddar: get.cheddar.me/app/FVESBGB

### Banking/Finance
- Chase code: J2SK9W (chase.co.uk/raf)
- Revolut code: ludoviv2sq!MAR1-26-AR-H2
- Wise: wise.com/invite/ahpc/albertob1508
- Moneybox: go.onelink.me/5M0L?pid=share&c=EN8YW8
- Plum: friends.withplum.com/r/RxK7c2fUNa
- Zopa code: ed204ce1b3dd265fa533
- iFAST: ifastgb.com/tellafriend/albertob367
- Tide code: 3834VA
- WorldFirst: s.worldfirst.com/2TuviC
- GlintPay code: X2PPG7-VF502
- Slide: slide.app.link/ho64MGlHF1b

### Investing
- Freetrade: magic.freetrade.io/join/alberto/6f308795
- Webull: webull-uk.com/s/zEUukbJam8GjmUx6yq
- Wealthify: invest.wealthify.com/refer/81122944
- Wealthyhood code: 1461h9hv
- IG: refer.ig.com/albertob-2757
- Robinhood: join.robinhood.com/albertb-d5dfe0

### Other
- Amex Biz Platinum: ref aLBERBf3Ob (130k pts)
- Avios: avios.mention-me.com/m/ol/yn2yt-alberto-bolla
- Octopus: share.octopus.energy/ocean-quoll-258
- TrainPal code: 03ba089c$00
- Lebara: aklam.io/hgY3HOvR
- Lloyds: token link (apply.lloydsbank.co.uk)
- Swagbucks rb=150886036
- Freecash: freecash.com/r/89cab33004

---

## Current App Features (April 2026)

### Offers System
- 47 hardcoded offers + JSON offers from all_deals.json (~120 total)
- 3-level offer flow: collapsed card → accordion (desc + code + guide button) → slide panel (full step guide)
- Offer card shows: logo (Google favicon), category label, name, effort, reward amount, "Guide +50XP" button
- Accordion click uses relative DOM traversal (not getElementById) to avoid duplicate ID bug
- Global click listener handles all offer card interactions

### Home Page
- Personal greeting: "Good morning/afternoon/evening, [username] 👋"
- Streak pill visible in greeting row
- Gaming hero card: animated £ counter + Bank/Invest/Cash breakdown + "Make £360 this week" CTA button
- App description (1 line, new users only)
- In Progress section (only when user has active offers)
- Playbook CTA banner
- Today's Money Plan (opens by default, full buildOfferCard cards)
- Featured Offers section removed (was duplicating Offers tab)

### Offers Tab
- Category rows (Netflix-style) as default view
- Search bar + filter pills
- Accordion cards with logo, name, effort, reward (yellow, 20px bold), Guide button
- Cashback Battle section with JamDoughnut featured first

### Playbook Tab
- 8 comprehensive guides (idiot-proof, plain English):
  1. 🏦 Bank Switch Bible (full CASS explanation, 7 steps, warnings)
  2. 💳 Cashback Complete Guide (3 methods: cards, gift apps, websites)
  3. 🛒 Supermarket Stacking (basic + advanced stack, real £ numbers)
  4. 📈 Free Shares Guide (Freetrade, Robinhood, Webull, hold periods)
  5. ⚡ Energy & Broadband Switching (Octopus, cashback stacking)
  6. 🔄 Direct Debit Setup Guide (what counts, cheap options)
  7. ⚡ Stack £500 in 90 Days (week-by-week plan with running totals)
  8. ⚠️ Common Mistakes (most important — read before starting)
- Plus: Gamification guide + Cashback Battle (live rates)
- Filter pills at top: All / Bank Switch / Cashback / Investing / Supermarket / Energy / Direct Debits / 90-Day Plan / Mistakes
- Each guide has: plain English intro, numbered steps, ⚠️ Warning box, 💡 Pro tip

### Progress Tab
Order: Pending Payouts → Money Tracker → Daily Check-in → Missions → Badges → Raffle

Money Tracker shows:
- Shield + level name ("3 Hunter") + gradient XP bar
- Streak pill
- Three coloured stat cards: Earned (green), Pending (amber), Available (neutral)

### Community Tab
Order: Reddit → Telegram → Direct Debit Service → Ko-fi → Email signup → Share (last)
- Direct Debit: opens slide-up guide panel (not external link)
- Share button: upload arrow SVG icon
- Email visible in footer: hello&#64;moneyhunters.co.uk

### Gamification
- XP system: +50 claim, +100 complete, +10 daily, +50 7-day streak
- Badges: First Claim, On Fire, Money Maker, Bank Buster, Elite Hunter
- Weekly missions
- Raffle (RAFFLE_ENABLED = false, launches at 25 users)
- Daily check-in with streak tracking

### Auth
- Supabase email/password
- `preCheckAuth()` runs synchronously on load (updates button before async)
- `onAuthStateChange` calls `updateUserBadge()` on SIGNED_IN
- Button shows username in green with sign-out action when logged in
- `updateGreeting()` shows username in home greeting

### Slide Panel (Full Guide)
- Opens when user taps "View Full Guide & Claim →"
- Shows: reward, badge, effort, description, referral code, step-by-step with checkboxes, tips, warnings, log savings
- "Next recommended offer" card at bottom (same category → any)
- Footer: big claim button that opens offer URL + awards XP

---

## UI/UX Improvements (April 2026 — Current Session)

This was a major UI overhaul session. Changes applied in order:

### Fix 1 — Offers Tab Accordion
- Moved `onclick` from `<article>` to `<div class="offer-card-top">`
- `toggleOfferCard` now uses `article.querySelector()` for accordion body (avoids duplicate ID bug)
- Global click listener catches `[data-offer-id]` and calls `toggleOfferCard`
- "View Full Guide" button uses `event.stopPropagation()` to open panel without triggering accordion

### Fix 2 — Community Tab
- Share card moved to last position
- Share icon: upload arrow SVG (not Android share nodes icon)
- Card order: Reddit → Telegram → Direct Debit → Ko-fi → Email → Share

### Fix 3 — Playbook
- Removed Reddit/Telegram mentions from Playbook tip
- Added filter pills at top for navigation between guides
- 8 new comprehensive guides replacing old 4 basic ones

### Fix 4 — Progress Tab Order
- Pending Payouts first
- Money Tracker second (with new visual stat cards)
- Daily Check-in third
- Then Missions → Badges → Raffle

### Fix 5 — Gaming Card (Home Hero)
- Filters out scraped/JSON offers (only curated hardcoded offers counted)
- Caps per-offer at £500 to prevent impossible numbers
- New tagline: "Bank switches, free shares and cashback — all in one place"
- Big green CTA button: "🎯 Make £360 this week — see how"

### Fix 6 — Auth State (Sign In button)
- `onAuthStateChange` now calls `updateUserBadge()` on SIGNED_IN event
- Sign out properly resets button style and onclick handler

### Fix 7 — Today's Money Plan
- Now renders full `buildOfferCard()` cards (not task-btn buttons)
- Opens by default (not collapsed)
- Tapping card opens accordion inline, "View Full Guide" opens slide panel

### Fix 8 — Progress Tab Visual Cards
- Level shield card with gradient XP bar and streak pill
- Three coloured stat hero cards: Earned (green gradient), Pending (amber gradient), Total (neutral)
- `renderProfile()` updated to populate new hero card IDs

### Fix 9 — Offer Cards View Guide Button
- "Guide +50XP" button always visible on card face (no accordion needed to find it)
- Right column has `min-width:80px` so button never collapses
- `event.stopPropagation()` prevents accordion from opening when button tapped

### Fix 10 — Bottom Nav SVG Icons
- Replaced emoji with clean Feather-style SVG icons
- House (Home), Search (Offers), Bar chart (Progress), Open book (Playbook), People (Community)
- Active tab: green colour + thicker `stroke-width: 2.5` + green pill background
- Nav has stronger shadow, no border

### Fix 11 — Topbar Slimmed Down
- Removed 4-stat row from header (was cluttering)
- Now: logo left + theme toggle + auth button right only
- Auth button pill-shaped (border-radius: 999px)
- Stat IDs kept in hidden div for JS compatibility

### Fix 12 — Personal Greeting
- `updateGreeting()` function added, called in `renderAll()`
- Shows: "Good morning/afternoon/evening" based on hour
- Username from `mh_username` localStorage or email prefix, fallback "Hunter 👋"
- Streak pill (amber) only shows if streak > 0

### Fix 13 — Home Page Tightened
- Featured Offers accordion removed from home (duplicated Offers tab)
- Today's Money Plan opens by default
- App description shortened to one line

### Fix 14 — Next Recommended Offer
- Appears at bottom of every slide panel guide
- Finds next offer in same category, falls back to any offer
- Shows logo, name, effort, reward — tapping opens that guide

### Fix 15 — No Borders Design System
- Cards: border removed, shadow only (`0 2px 12px rgba(0,0,0,.3)`)
- Offer cards: border removed, shadow + hover lift
- Topbar: `box-shadow: 0 1px 0 rgba(255,255,255,.04), 0 4px 16px rgba(0,0,0,.3)`
- Bottom nav: shadow replaces border
- `--line` reduced from `.07` to `.04` opacity
- Border radius bumped to 18px on cards and offers
- Added `--shadow-lg` variable for elevated panels

### Fix 16 — Spacing & Padding
- Section margin: 24px
- Offer card top: 16px/18px padding
- Offer card accordion body: 18px padding
- Community/milestone cards: 18px padding
- Side padding: 14px (was 10px)
- Offer logo: 40px (was 36px), border removed

### Fix 17 — Typography Hierarchy
- Reward amounts: yellow (`var(--yellow)`), 20px, 900 weight, tight tracking
- Category labels: muted grey (not green — green was fighting reward for attention)
- Section titles: 18px, 800 weight, tighter tracking
- Offer names: 15px, 700 weight
- Guide card titles: 16px, 800 weight
- Community h3: 17px, 800 weight, more line-height on p text

---

## Known Issues / Pending

1. **Cloudflare email obfuscation**: Cloudflare rewrites `hello@moneyhunters.co.uk` in index.html — use `&#64;` for @ sign as workaround. Disable in Cloudflare dashboard: Scrape Shield → Email Address Obfuscation → Off
2. **Logos not showing**: Some favicons (Lloyds, Freetrade) not loading via Google favicon service — custom logo upload planned
3. **index.html email**: Already correct in GitHub source. Cloudflare rewrites on serve.
4. **Cline recurring issue**: Creates junk temp files, may revert to backups — always run `git log` before trusting Cline's reports

---

## Workflow Notes

- Claude is used for architecture, complex logic, and larger feature builds
- Cline + DeepSeek for mechanical code edits
- Always syntax check JS before pushing: extract JS with Python, run `node --check`
- Test on live site after each GitHub push — hard refresh on mobile: hold refresh → Hard Reload
- Reset onboarding for testing: `localStorage.removeItem('mh_onboarded_v2')` in console
- British English throughout, £ not $

---

## Next Steps (Priority Order)

1. Push current app.html to GitHub and test all fixes on live site
2. Upload brand logos (Lloyds horse, Freetrade etc.) as PNG files to repo
3. Post on r/beermoneyuk to get first real users
4. Draft message to beermoneyuk/Scrimpr owner for review/feedback
5. Apply to CJ Affiliate
6. Follow up Tillo/JamDoughnut B2B API
7. Raffle launch at 25 users (set `RAFFLE_ENABLED = true`)

---

## Last Updated
- **Memory Bank Created**: March 27, 2026
- **Memory Bank Updated**: April 11, 2026
- **Major Session**: April 2026 — Full UI/UX overhaul (17 fixes applied)
- **App state**: Stable, syntax-checked, ready to push
- **Working file**: `/mnt/user-data/outputs/app.html`
- **index.html**: `/mnt/user-data/outputs/index.html` (email fixes applied)

---

*This memory bank serves as a living document for the MoneyHunterUk project. Update regularly as the project evolves.*
