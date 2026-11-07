# Promo content generator (Coinsworth / Money Hunters social posts)

Scripts used to auto-produce TikTok/Reels/Shorts videos and Instagram images from the real game (`/play/`) and app (`/app.html`). Built Nov 2026.

## Setup (in a working folder, e.g. a scratchpad)
```
cp -r scripts/promo/* <WORKDIR>/ && cd <WORKDIR>
sed -i "s#__WORKDIR__#$PWD#g" *.js *.py local.css && mkdir -p fonts && mv local.css fonts/
(cd fonts && npm i @fontsource/press-start-2p @fontsource/pixelify-sans @fontsource/inter)
mkdir sb && (cd sb && npm i @supabase/supabase-js@2)   # only for app recordings
# serve the repo root on :8766, e.g. `python3 -m http.server 8766` from the repo
```
Needs Playwright + Chromium, ffmpeg, Python with numpy.

## Pieces
- `lib.js` - opens the game at 1080x1920 (zoom 2.5 trick, native-res frames), routes Google Fonts to local copies, blocks Umami, records via CDP screencast with timing marks.
- `drive.js` - tap helper with visible tap ripple; generic battle driver (`fight`).
- `override.js` - forces specific question ids via pickQ.
- `cap.js caps/<spec>.json` - renders caption PNG overlays (hook / mid / end-card styles).
- `compose.py <framesdir> <out.mp4> <overlays.json> [end]` - frames + overlays -> H.264 1080x1920. `SAFE=1` shrinks gameplay into the middle so TikTok/IG UI never covers answers. First overlay at t=0 has no fade, so frame 1 (TikTok's default cover) shows the hook.
- `multi.py` - concatenates segments/time ranges from several recordings.
- `quizbatch.js` + `quizlist.json` - daily quiz videos (question id, boss, hook index).
- `funnyrec.js` + `funnylist.json` - "POV" villain meme videos.
- `cards.js` - Spot-the-scam carousels (4:5) + money fact cards. `vcards.js` + `sprites.js` - villain trading cards. `sotw.js` - bank switch of the week card. `appclip.js` - app walkthrough recording.
- `chip.py` - generates original royalty-free chiptune loops (tune_bouncy/sneaky/upbeat).
- `base_save.json` - a save just after the intro, used as the starting point for recordings.

## Content rules
- Facts must be true, sourced and conditional; referral links disclosed ("Ad"); never "free money"; not financial advice.
- Posting: ~2/day. Quiz video 12:30, funny/app video 19:00; images mainly Instagram/Facebook.
- TikTok: use silent versions + the sound "Cute and fun 8bit. Streaming, game commentary(1624766)" (Vlog Music Crafts) on every video.
