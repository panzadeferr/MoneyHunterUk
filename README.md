# Money Hunters UK

Free UK money-deals tracker: bank switches, cashback, referrals, free shares.
Live at https://moneyhunters.co.uk (GitHub Pages).

## How it works
- `app.html` — the PWA app (all inline JS/CSS), fed by `all_deals.json`
- `index.html` — landing page
- `scraper.py` — Python scraper: manual offers + Google News + HotUKDeals + Megalist + Scrimpr
- `.github/workflows/scraper.yml` — runs the scraper every 6h, commits `all_deals.json`, triggers deploy
- `.github/workflows/deploy.yml` — tests + deploys to GitHub Pages

## Local run
```
pip install -r requirements.txt
python scraper.py
```

Telegram alerts: set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` repo secrets.
