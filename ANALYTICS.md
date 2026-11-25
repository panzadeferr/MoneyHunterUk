# Analytics (Umami)

Website id `f9d2c068-643f-4cfc-847e-c22fec24bafe`. Pages call `window.mhTrack(name, data)`, a safe wrapper around `umami.track`.

## Own visits
`?mh_me=1` sets `localStorage.umami.disabled=1` before the Umami script loads, so that browser is not counted. `?mh_me=0` clears it. Umami documents this flag in its tracker settings ("Excluding your own visits"). Checked by `tests/check_tracking.py`.

## Events
| New event | Old event (kept until 4 Dec 2026) | Fired when | Data |
|---|---|---|---|
| `play-start` | `game_new`, `game_continue` | a player enters the game world | `mode`: new or continue |
| `game-complete` | `game_finished` | the first time the build ending is reached | none |
| `offer-click` | `offer_opened` (app), `outbound_click` (offers, bank-switch) | an offer card is opened in the app, or an outbound link is clicked | `offer`: offer name, max 60 chars |
| `newsletter-submit` | none | `newsletter-thanks.html` loads after the Brevo double opt-in form | `page` |
| `share-click` | `share_clicked` | a player taps share after a boss | `boss`, max 60 chars |

After 4 Dec 2026 remove the old names (`game_new`, `game_continue`, `game_finished`, `offer_opened`, `outbound_click`, `share_clicked`) and keep the new ones.

## Campaign links
The end-of-game link uses `?utm_source=coinsworth&utm_medium=game&utm_campaign=end_screen`. The share link uses `?utm_source=share`.

## Newsletter redirect
`newsletter-thanks.html` is `noindex` and not in the sitemap. In Brevo, set the form's confirmation redirect to `https://moneyhunters.co.uk/newsletter-thanks.html` (this is a manual step in Brevo).

## Notes
Event data contains no personal data. Keep `.github/workflows/deploy.yml` copy list in sync when adding pages (`tests/check_deploy.py`).
