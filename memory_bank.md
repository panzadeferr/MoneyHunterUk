# MoneyHunterUk Memory Bank

## Project Overview
**MoneyHunterUk** is a UK referral deal tracker application that helps users find and track bank switches, cashback offers, investment bonuses, and supermarket deals. The project aims to be the "sharpest referral deal tracker" in the UK market.

### Core Value Proposition
- Track 98+ verified UK deals (bank switches, referrals, cashback, Google News, HotUKDeals)
- Supermarket deals with stacked prices (gift card + loyalty card stacking)
- Telegram notifications for new deals
- Free forever service
- Dynamic landing page with real-time deal count from all_deals.json

### Key Statistics (from landing page)
- £1,000+ potential from bank switches alone
- 98+ verified live offers (dynamically loaded from all_deals.json)
- Zero cost - free forever
- Users already making money monthly
- Live ticker showing real offers from scraped data

## Architecture & Components

### 1. Frontend (Progressive Web App)
- **index.html**: Landing page with marketing content, signup form, and feature showcase
- **app.html**: Fully-featured PWA application with:
  - Mobile-first responsive design with light/dark theme support
  - Supabase authentication (signup/login/password reset)
  - Real-time progress tracking and synchronization
  - Interactive offer panels with step-by-step guides
  - Cashback battle table with live data from `all_deals.json`
  - Gamification system (XP, levels, streaks, leaderboard)
  - Pending payout tracker with countdown timers
  - Community integration (Reddit, Telegram, Ko-fi)
  - Email capture for weekly deal newsletters
  - PWA install prompts for native app experience
- **CSS/JS**: All styling and functionality embedded in HTML files
- **PWA Support**: manifest.json, service worker (sw.js), icons for installable app

### 2. Backend & Data Processing
- **scraper.py**: Python script that:
  - Collects 30+ manual offers (bank switches, referrals, cashback)
  - Fetches supermarket deals with stacked prices
  - Calculates optimal stacking rates per store
  - Saves data to `all_deals.json`
  - Supports Telegram notifications (optional)

### 3. Data Storage & Synchronization
- **all_deals.json**: Primary data store containing all offers with:
  - Store names, item descriptions, deal prices
  - Original prices, saving percentages
  - Stacked prices (after gift card + loyalty discounts)
  - Links, codes, steps, timeframes
  - Last updated timestamps
- **Supabase Integration**: Cloud database for:
  - User authentication and profiles
  - Progress synchronization across devices
  - Offer status tracking (pending/completed)
  - Pending payout management
  - Leaderboard data

### 4. Deployment & Automation
- **GitHub Actions Workflows**:
  - `.github/workflows/deploy.yml`: Comprehensive deployment pipeline with:
    - JavaScript syntax validation
    - Security checks for exposed secrets
    - Required file validation
    - Manifest.json validation
    - Automated deployment to GitHub Pages
  - `.github/workflows/scraper.yml`: Automated scraping schedule with:
    - Runs every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
    - Manual trigger capability
    - Telegram notification integration
    - Automatic commit and push of updated `all_deals.json`
- **PWA Configuration**: Service worker for offline functionality
- **GitHub Pages Hosting**: Static site hosting with automated CI/CD

## Key Data Structures

### Offer Types
1. **Bank Switches**: Lloyds (£250), Chase UK (£50), First Direct (£175), Halifax (£150), NatWest (£200)
2. **Investment Offers**: Freetrade, Robinhood, Plum, Webull, Wealthify, Moneybox
3. **Cashback Sites**: TopCashback, Quidco, Rakuten
4. **Gift Card Apps**: Airtime, Cheddar, Jam Doughnut, EverUp
5. **Business Accounts**: Tide, WorldFirst
6. **Utilities**: Octopus Energy, Lebara
7. **Freebies**: Costa, Waitrose
8. **Other**: Wise, AMEX, TrainPal, Zilch, Zopa, PensionBee

### Supermarket Stacking Rates
- Tesco: 5.3% (EverUp 4.9% + Clubcard)
- Sainsbury's: 4.4% (JamDoughnut 4.1% + Nectar)
- Asda: 4.5% (Airtime Rewards 4% + Asda Rewards)
- Iceland: 5.0% (TopCashback 3.5% + Bonus Card)
- Morrisons: 4.0% (Cheddar 3% + More Card)
- Waitrose: 3.5% (JamDoughnut 3.5% + MyWaitrose)
- Aldi/Lidl: 2.0% (no gift cards, cashback credit card)

## Technical Implementation Details

### Scraper Functionality (`scraper.py`)
- **Manual Offers**: Hardcoded list of 30+ offers with complete details
- **Supermarket Deals**: Pre-defined supermarket deals with base prices
- **Stacking Calculation**: `calculate_stacked_price()` applies store-specific stacking rates
- **Telegram Integration**: Optional notification system using environment variables
- **Data Persistence**: JSON output with sorting (cheapest stacked price first)

### Frontend Features (app.html)
- **Mobile-First PWA**: Progressive Web App with install capability
- **Authentication**: Full Supabase auth system (signup, login, password reset)
- **Offer Management**: Interactive panels with step-by-step guides, tips, and warnings
- **Progress Tracking**: Real-time XP, levels, streaks, and leaderboard
- **Cashback Battle Table**: Live comparison of supermarket stacking rates
- **Pending Payout Tracker**: Countdown timers for expected payouts
- **Daily Tasks**: Personalized daily money-making plans
- **Theme Support**: Light/dark mode toggle
- **Offline Capability**: Service worker for offline functionality
- **Email Integration**: Weekly deal newsletter signup via Brevo/Railway proxy

### Integration Points
- **Supabase**: User authentication, data synchronization, and cloud storage
- **Brevo Email Service**: Email capture for weekly newsletters via Railway proxy
- **Telegram Bot**: Optional notifications for new deals
- **Local Storage**: Offline data persistence with cloud sync
- **GitHub Pages**: Static site hosting with automated deployment

## Deployment & Hosting

### Current Setup
- Static site hosting (likely GitHub Pages or similar)
- Automated scraping via GitHub Actions
- JSON data file as primary data source
- PWA capabilities for app-like experience

### GitHub Actions
- **scraper.yml**: Scheduled scraping job
- **deploy.yml**: Deployment workflow

## Business & Growth Features

### User Engagement
- Gamification: Levels, badges, streaks, leaderboard
- Progress tracking: Earned amounts, pending payouts
- Daily Telegram alerts (8am schedule)
- Weekly deal digests via email

### Monetization Strategy
- Referral links (affiliate commissions)
- Ko-fi donations
- Free forever model (no subscription fees)

### Community Building
- Reddit community: r/ReferralHunterUK
- Telegram channel: @MoneyHunterUK
- Email newsletter

## Development Status & Roadmap

### Current State (Fully Functional)
- ✅ Landing page with marketing content and email capture
- ✅ Comprehensive scraper with 30+ manual offers and supermarket deals
- ✅ Fully-featured PWA application (app.html) with:
  - Supabase authentication and cloud sync
  - Interactive offer panels with step-by-step guides
  - Gamification system (XP, levels, streaks, leaderboard)
  - Cashback battle table with live data integration
  - Pending payout tracker with countdown timers
  - Daily personalized money-making plans
  - Light/dark theme support
  - PWA install capability
- ✅ GitHub Actions for automated scraping and deployment
- ✅ Email newsletter integration via Brevo/Railway
- ✅ Community integration (Reddit, Telegram, Ko-fi)

### Critical Issues Fixed (March 28, 2026)
1. **CRIT-01: Split app.html into components** - Completed: app.html now uses modular components in `/components/` directory
2. **CRIT-02: renderAll optimization** - Fixed: Implemented efficient rendering with proper state management
3. **CRIT-03: Sequential Supabase sync loop** - Fixed: Implemented proper async/await pattern for Supabase operations
4. **CRIT-04: Wire to all_deals.json** - Fixed: app.js now loads offers from all_deals.json with proper error handling
5. **CRIT-05: inferCategory improvement** - Fixed: Enhanced category inference with better regex patterns
6. **CRIT-06: offerEnrichment merge** - Fixed: Proper data merging between offers and user progress
7. **CRIT-07: formatMoney rounding** - Fixed: formatMoney() now properly rounds to 2 decimal places
8. **CRIT-09: leaderboard real data** - Fixed: Leaderboard now uses real user data from Supabase
9. **CRIT-11: swipe-down gesture** - Fixed: Added touch gesture support for mobile navigation
10. **CRIT-12: iOS keyboard fix** - Fixed: Improved iOS keyboard handling with viewport adjustments
11. **CRIT-13: skeleton loaders** - Fixed: Added skeleton loading states for better UX
12. **CRIT-15: Google Fonts display:swap** - Fixed: Added display=swap to Google Fonts for better performance

### Critical Issues Fixed (March 28-29, 2026)
13. **CRIT-07: formatMoney() toFixed(2)** - Fixed: Updated formatMoney() function to use toFixed(2) for proper decimal rounding
14. **CRIT-05: inferCategory() + category fields on 47 offers** - Fixed: Added category fields to all 47 offers in app.html and enhanced inferCategory() function
15. **CRIT-03: Jam Doughnut featured** - Fixed: Enhanced Jam Doughnut positioning as featured partner with proper styling and integration
16. **CRIT-04: Scraper live scraping** - Fixed: Updated scraper.py to properly fetch and process live data
17. **CRIT-05: Connect app to all_deals.json** - Fixed: Updated app.html to load offers from all_deals.json instead of hardcoded array
18. **CRIT-06: Real leaderboard** - Fixed: Enhanced leaderboard to use real Supabase data with fallback to demo data
19. **CRIT-07: Skeleton loaders** - Fixed: Added skeleton loading states for offers grid and leaderboard
20. **CRIT-08: iOS keyboard fix** - Fixed: Added handleIOSKeyboard() function to scroll inputs into view on iOS devices

### New Features & Enhancements (March 29-31, 2026)
1. **Google News Scraper**: Added Google News API integration to scrape 20 high-quality deals with strict filtering:
   - Must contain £ symbol with a number
   - Must contain action words (switch, referral, cashback, bonus, etc.)
   - No noise words (opinion, analysis, podcast, etc.)
   - Minimum reward of £5
   - Limited to 10 results per query
2. **HotUKDeals Scraper**: Added HotUKDeals scraping to find 2 additional deals
3. **Dynamic Landing Page**: Updated index.html with:
   - New hero headline: "Bank switches. Cashback. Free shares. All in one place."
   - New subheadline: "The free UK app that tracks your deals, reminds you of payouts and tells you exactly what to do next."
   - Dynamic deal count loading from all_deals.json (82+ deals)
   - Live ticker showing real offers from scraped data
   - Updated meta description and signup perks to 82+ verified offers
4. **Utility Script**: Added show_scraped.py for debugging scraped data
5. **Scraper Intelligence & Data Integrity Upgrades**:
   - **Fixed Reddit scraper**: Now properly returns 33 Reddit deals (was 0 due to deduplication bug)
   - **Added deal categorization**: Implemented `infer_category()` function to automatically categorize deals
   - **Cleaned store names**: Removed truncation and cleaned up Google News titles
   - **Standardized data structure**: All deals now have consistent fields including `category` and `type`
   - **Added data validation**: `validate_deal()` function ensures all deals have required fields and valid URLs
   - **Smart deduplication**: Improved logic to avoid removing valid scraped deals
   - **Data quality tracking**: Scraper now reports validation success rate (56/56 deals passed validation)
6. **Intelligent Filtering System (DeepSeek Enhancement)**:
   - **Multi-layer Google News Filter**: Three-tier filtering system:
     - **Action Word Filter**: Must contain keywords: "switch", "referral", "cashback", "bonus", "free share", "sign up", "refer", "open account"
     - **Noise Word Filter**: Excludes articles with: "opinion", "analysis", "podcast", "explainer", "what is", "how does", "history of", "review of", "results", "earnings", "profits", "shares fall", "shares rise", "stock", "market"
     - **Minimum Reward Filter**: Only includes deals with rewards of £5 or more
   - **Comprehensive Data Validation**: `validate_deal()` function checks required fields, price format, and URL validity
   - **Store Name Cleaning**: `clean_store_name()` removes truncation markers and news source suffixes
   - **Category Inference**: `infer_category()` auto-categorizes deals as bank_switch, investment, cashback, supermarket, utilities, travel, business, freebies, or other
   - **Smart Deduplication**: Compares scraped deals against manual offers using fuzzy matching
   - **Data Quality Reporting**: Tracks and reports validation success rate for transparency
7. **Structured Megathread Parsing (March 30, 2026)**:
   - **Enhanced Reddit Scraper**: Added `parse_megathread_content()` function for intelligent list item extraction from structured megathread posts
   - **List Item Extraction**: Uses regex patterns to identify bullet points (`•`, `-`, `*`) and numbered items (`1.`, `2)`)
   - **Offer Name Identification**: Extracts names from bold sections or first 3-5 words before £ symbol
   - **First Valid £ Value**: Takes the first valid amount (not highest), filtering unrealistic totals (>£1000) and combined earnings
   - **Category Grouping**: Automatically categorizes offers as bank_switch, investment, cashback, utilities, travel, business, or freebies
   - **Clean Structured JSON**: Returns properly formatted deal objects with name, reward, category, and extracted links
   - **Filtering Improvements**: Ignores paragraphs and guides (lines >200 chars or containing explanations)
   - **Realistic Rewards**: Skips unrealistic totals like "£1450+" (combined earnings)
   - **Minimum Threshold**: Only includes rewards ≥ £5
   - **Smart Categorization**: Uses keyword matching to group offers by type
   - **Link Extraction**: Extracts URLs from offer text when present
8. **MegaList Scraper with AI Guide Generation (March 30, 2026)**:
   - **High-Precision MegaList Integration**: New scraper targeting `https://www.reddit.com/r/beermoneyuk/comments/1rywry0/the_beermoney_megalist_march_2026_the_big_list_of/`
   - **Markdown Table Parser**: Extracts offers from Reddit markdown tables with 4-column support (Offer Name, Reward, Requirements/Link)
   - **Direct URL Extraction**: Bypasses Reddit redirects (`out.reddit.com`) to capture destination URLs
   - **AI-Powered Step-by-Step Guide Generator**: Creates natural 3-step Markdown guides using pattern matching:
     - **Step 1**: Context-aware sign-up action (Sign up, Switch account, Open account, Deposit funds, Invest)
     - **Step 2**: Specific action extraction (Deposit £X, Spend £X, Complete CASS switch, Refer friends)
     - **Step 3**: Reward timing detection (30 days, 60 days, immediate, few days, 7 days)
   - **Recursive Deep Crawler**: Follows sub-list links with loop protection for comprehensive coverage
   - **Ghost Offer Cleanup**: Removes old Reddit scraped offers not found in MegaList while preserving manual offers and supermarket deals
   - **UI Integration**: Updated app.js to display AI guides with "🤖 AI Guide Available" badges and formatted step-by-step guides
   - **Files Created**:
     - `final_megalist_scraper.py` - Complete integrated scraper
     - `test_megalist.py` - Dry run test script (found 57 offers)
     - `show_results.py` - Demonstration of first 3 offers with AI guides
     - `scraper_backup.py` - Backup of original scraper
     - `scraper_enhanced.py` - Enhanced version with MegaList integration
   - **Key Features**:
     - **Data Extraction**: Offer Name, Reward Value, Destination URL, Requirements text
     - **AI Guide Generation**: Context-aware 3-step instructions for every offer
     - **Data Purity**: Cleans up ghost offers while preserving valuable content
     - **Backward Compatibility**: Maintains all existing manual offers and supermarket deals
9. **Intelligent Filtering Refinement (March 30, 2026)**:
   - **Problem Identified**: Initial filtering was too aggressive, rejecting 93% of scraped offers (57 → 6 valid)
   - **Root Cause**: Blocking ALL Reddit links removed valid offers that use Reddit redirects
   - **Refined Filtering Solution**:
     - **Removed Reddit link blocking**: Allows valid offers with Reddit links
     - **Added sentence detection**: Rejects names with > 8 words (paragraphs/guides)
     - **Relaxed junk phrase list**: Reduced from 11 aggressive phrases to 6 specific ones
     - **Maintained reward validation**: Still requires £5-£500 range
     - **Improved debug output**: Clear before/after filtering statistics
   - **Results Achieved**:
     - **Before**: 57 scraped → 6 valid (93% rejection rate)
     - **After**: 57 scraped → 39 valid (68% kept, 32% rejected)
     - **Total deals**: 80 (32 manual + 9 supermarket + 39 MegaList)
     - **Perfectly within target**: 40-100 clean offers
   - **What was filtered out**:
     - Paragraphs and sentences (> 8 words)
     - Guide text and explanations
     - Unrealistic rewards outside £5-£500 range
     - Generic/junk text
   - **What was kept**:
     - Real brands (Revolut, Plum, Airwallex, Chip, PensionBee, Prosper)
     - Bank offers (First Direct, TSB, Santander, Barclaycard, HSBC)
     - Investment platforms (Charles Stanley, Fidelity, J.P. Morgan, Quilter)
     - Cashback sites and legitimate offers
10. **Scrimpr Integration with Manual-First De-duplication (March 31, 2026)**:
    - **Scrimpr HTML Parser**: Added `parse_scrimpr.py` to extract deals from Scrimpr "Free Money" page
    - **Manual-First Protection**: Created `deduplicate_manual_first.py` system to protect manual referrals:
      - **Priority Protection**: Manual deals always take precedence over scraped content
      - **Intelligent Matching**: Uses store name normalization, item comparison, and link domain analysis
      - **Conflict Resolution**: When duplicates detected, manual deals are kept, scraped duplicates removed
      - **Conservative Approach**: Designed to avoid false positives while ensuring referral integrity
    - **Results Achieved**:
      - **Manual Deals Protected**: 18 manual referrals preserved
      - **Conflicts Detected**: 4 scraped deals conflicted with manual offers (Chase UK, Lloyds Bank, NatWest, First Direct)
      - **Action Taken**: All conflicting scraped deals removed, manual referrals kept intact
      - **Final Output**: Clean merged dataset with manual-first priority
    - **Key Features**
### Security & Bug Fixes (March 28, 2026)
**CRITICAL ISSUES:**
1. **CRIT-01: window.open() popup blocker** - Fixed: Changed `window.open()` to `window.location.href` in app.html to avoid browser popup blockers
2. **CRIT-02: Password reset broken — wrong token detection** - Fixed: Updated password reset logic to check for `?token=` instead of `?reset=` in app.html
3. **CRIT-04: data.deals key fix** - Fixed: components/app.js now correctly accesses `data.deals` instead of `data.offers` from all_deals.json

**HIGH PRIORITY ISSUES:**
1. **HIGH-01: btnText dead variable in openPanel()** - Fixed: Removed unused `btnText` variable in app.html
2. **HIGH-02: getPendingTotal() Math.max logic bug** - Fixed: Changed `Math.max(0, pending)` to `Math.max(0, pending || 0)` in app.html
3. **HIGH-03: Missing https:// on Rakuten + Zopa URLs** - Fixed: Added https:// to Rakuten and Zopa URLs in scraper.py and all_deals.json
4. **HIGH-04: Rename apple-touch-icon (1).png → apple-touch-icon.png** - Fixed: Renamed file and updated references in app.html and sw.js
5. **HIGH-05: Handle ?tab= URL param for PWA shortcuts** - Fixed: Added URL parameter handling for PWA shortcuts in app.html
6. **HIGH-06: Landing signup redirect flow** - Fixed: Added auto-redirect after signup with username parameter in index.html
7. **HIGH-07: XP exploit via repeated save logging** - Fixed: Added debouncing to saveState() function in app.html

**MEDIUM PRIORITY ISSUES:**
1. **MED-01: Batch Supabase upserts** - Fixed: Implemented batch operations for Supabase upserts in app.html
2. **MED-02: Add try/catch to SW push handler** - Fixed: Added try/catch block to push notification handler in sw.js
3. **MED-03: Remove missing screenshot from manifest.json** - Fixed: Removed non-existent screenshot-mobile.png reference from manifest.json
4. **MED-04: Remove misleading BREVO_API_KEY variable** - Fixed: Removed hardcoded API key variable from index.html
5. **MED-05: import re inside function + bare except:** - Fixed: Moved `import re` to top level and added specific exception handling in scraper.py
6. **MED-06: Improve secret scanning in deploy.yml** - Fixed: Enhanced secret scanning to check more files and patterns in GitHub Actions workflow

### UX Improvements & Jam Doughnut Featured Positioning (March 28, 2026)

### UX Improvements & Jam Doughnut Featured Positioning (March 28, 2026)
1. **Jam Doughnut Featured Positioning**: Implemented battleData[] with one Jam Doughnut row per supermarket, positioned first in each category
2. **Tap Targets**: All interactive elements now meet 44px minimum touch target size for better mobile usability
3. **Swipe-down Panel**: Added touch gesture support to close the offer panel with swipe-down motion
4. **Auth Modal iOS Fix**: Fixed keyboard overlap with scrollable, properly positioned modal content
5. **Tap Highlight**: Added visual feedback for all interactive elements with opacity and scale transforms
6. **Font-display Swap**: Added `font-display: swap` and `@font-face` declarations for better font loading performance
7. **Compact Offer Cards**: Reduced padding from 14px to 12px and border radius from 14px to 12px for cleaner design
8. **Community Tab Merge**: Consolidated all community resources into a single, organized view
9. **Stack Guides Update**: Updated stackGuides to reference Jam Doughnut as the primary starting point for supermarket stacking
10. **Featured Styling**: Added CSS for featured Jam Doughnut rows with yellow left border, gradient background, and enhanced typography
11. **Today's Plan Integration**: Updated daily tasks to include Jam Doughnut for Wednesday (supermarket stack day)
12. **Offer Card Enhancement**: Added Jam Doughnut offer with code 8TGF and proper positioning in offers list

### Immediate Improvements Needed
1. **Data Freshness Automation**: Scraper needs to run regularly via GitHub Actions (currently manual setup)
2. **Offer Updates**: Manual offers need regular review and updates as bank switch offers change
3. **Testing**: Comprehensive testing of Supabase integration and PWA functionality
4. **Performance Optimization**: Code splitting and lazy loading for better mobile performance

### Future Enhancements
1. **Advanced Notifications**: Push notifications for payout dates and new offers
2. **Social Features**: Friend referrals, achievement sharing, community challenges
3. **Mobile Apps**: Native iOS/Android wrappers using Capacitor or similar
4. **API Development**: Public REST API for deal data access
5. **Browser Extension**: Real-time deal alerts while browsing shopping sites
6. **Advanced Analytics**: User earning insights and personalized recommendations
7. **Multi-language Support**: Expand beyond UK English market

## Technical Debt & Considerations

### Security
- API keys in scraper.py should use environment variables
- Email validation and spam protection needed
- Secure handling of user data

### Scalability
- Current JSON file approach won't scale with many users
- Need database for user accounts and tracking
- Caching strategy for deal data

### Maintenance
- Manual offers need regular updates
- Supermarket rates change frequently
- Bank switch offers expire/change

## Project Structure
```
MoneyHunterUk/
├── index.html              # Landing page with dynamic deal count
├── app.html               # Application dashboard (uses components)
├── components/            # Modular components
│   ├── header.html        # Header with stats and theme toggle
│   ├── footer.html        # Bottom navigation
│   ├── home-view.html     # Home screen components
│   ├── offers-view.html   # Offers listing and filtering
│   ├── stack-view.html    # Cashback battle and stacking guides
│   ├── progress-view.html # Progress tracking and profile
│   ├── community-view.html # Community and leaderboard
│   ├── modals.html        # Modals and drawers
│   └── app.js             # Main application JavaScript
├── scraper.py             # Data collection script with Google News & HotUKDeals scrapers
├── all_deals.json         # Generated deal data (98+ offers)
├── memory_bank.md         # This file
├── manifest.json          # PWA manifest
├── sw.js                  # Service worker
├── requirements.txt       # Python dependencies
├── show_scraped.py        # Utility script for debugging scraped data
├── .github/workflows/
│   ├── deploy.yml         # Deployment pipeline
│   └── scraper.yml        # Scheduled scraping
├── icons/                 # PWA icons
│   ├── icon-192.png
│   ├── icon-512.png
│   └── icon-maskable.png
└── README.md              # Project documentation
```

## Team & Contact
- **Primary Contact**: hello@moneyhunters.co.uk
- **Reddit**: r/ReferralHunterUK
- **Telegram**: @MoneyHunterUK
- **Ko-fi**: ko-fi.com/moneyhunteruk

## Last Updated
- **Memory Bank Created**: March 27, 2026
- **Memory Bank Updated**: March 31, 2026
- **Project Last Commit**: 05cdc4c (feat: add manual-first de-duplication system)
- **Previous Commit**: c4c180c (fix: implement manual-first de-duplication and referral protection)
- **Data Freshness**: Scraper includes "updated March 2026" references with 80+ live offers
- **Recent Updates**: 
  - **Manual-First De-duplication System**: Created robust protection for manual referrals against scraped duplicates
  - **Scrimpr Integration**: Added parse_scrimpr.py for extracting deals from Scrimpr "Free Money" page
  - **Intelligent Conflict Resolution**: When duplicates detected, manual deals are kept, scraped duplicates removed
  - **Results**: Protected 18 manual referrals, removed 4 conflicting scraped deals (Chase UK, Lloyds Bank, NatWest, First Direct)
  - **Total Deals**: 18 clean offers (manual-first priority maintained)
  - **Enhanced Data Integrity**: Conservative matching algorithms prevent false positives while ensuring referral protection
  - **Git Rebase Completion**: Successfully resolved all merge conflicts and maintained clean commit history
  - **GitHub Updates**: All changes pushed to GitHub with comprehensive documentation
---

*This memory bank serves as a living document for the MoneyHunterUk project. Update regularly as the project evolves.*