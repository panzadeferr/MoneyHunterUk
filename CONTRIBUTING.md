# Contributing to Money Hunters UK

## Ground rules
- Work on branches, open PRs. No direct pushes to main. CI (deploy.yml) tests every PR; only approved main pushes deploy.
- Never commit secrets or API keys. CI scans for known key formats.
- Keep the live site and the scraper working at all times. scraper.yml auto-commits scrape updates to main, so avoid long-lived local edits to all_deals.json and expect merge conflicts there.
- Zero budget: free tools only. Nothing with a cost without the maintainer's explicit approval.

## Editing app.html (parts-based method)
app.html is a single ~366 KB file: about 3,000 lines of CSS in the head, five view sections (home, offers, stack/Playbook, progress, community), and ONE main inline <script> (lines ~3975-7598) holding all JavaScript.

- Edit in self-contained parts: one CSS block, one view's HTML, or one JS function group at a time. Keep the skeleton untouched: exactly one Supabase CDN script tag (line 18) and exactly one main inline script tag.
- Never reformat, reindent or beautify the whole file. A formatting pass can corrupt the main script tag; the CI syntax check will catch it, but it wastes a PR round.
- Prefer targeted string replacements over rewriting blocks you don't need to touch.
- After every change, verify the main script still parses (node syntax-check.mjs, or the CI job) and that the required functions (renderAll, saveState, openPanel, initAuth, pushProgressToSupabase, ...) still exist.
- New JS goes in a clearly-commented function block near related code, called from the boot block at the end of the main script (after preCheckAuth).
- For larger restructures, the maintainer assembles app.html from parts; discuss the split in a PR first rather than reformatting in place.

## Data files
- /data/ holds game content: questions.json (question bank, batched) and playbook.json (Playbook chapters and articles). Game features load these files; do not hardcode question content in app.html or the game.
- /game/ holds the browser game: vanilla JS modules (world, battle, data, save) plus Tiled-authored map JSON, self-hosted, no CDN runtime dependencies.
- tests/check_data.py validates both files when present (unique ids, answer index in range, learn_more pointing at a real playbook article) and warns when a volatile question is past its review_by date.
- deploy.yml copies /data/ and /game/ into the site build when the directories exist.

## Service worker
- sw.js: documents are network-first; all_deals.json and /data/*.json are always network-first (never serve stale); static assets are cache-first. Bump the CACHE version whenever cached content semantics change.
