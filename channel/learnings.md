# Learnings (newest first)

## 2026-11-22 Sunday: first weekly long video (L001) + long-video engine + thumbnail playbook
- New: engine/render_long.py + engine/make_long.py (stock | voice | render | thumb | check) for 1920x1080 4-6 min videos;
  fetch_stock.py takes "orientation": "landscape"; engine/thumbnail_long.py makes 3 options + a phone-size compare sheet.
- Thumbnail research -> channel/thumbnail_playbook.md (12 rules). vidIQ niche scan (15 credits, 100 left): AI-news
  leaders use one hero + 2-3 huge words; small-channel breakouts lean on FREE / a big number; thumbnail swaps that doubled
  views replaced busy UI screenshots with a big product subject + 2-3 words.
- L001 thumbnail options: A "AI AGENT FOR $0" (phone photo), B giant "5" + "FREE AI UPGRADES THIS WEEK", C "GOOGLE AI 2.5X
  FASTER" (Hydrogen press art). Chose B: the biggest single subject, still readable at 168x94, brightest, true curiosity
  gap (which 5?), does not repeat the title. A's stock face looked calm/neutral; C's hero was small and niche.
- Fact check correction: Short 008 said Ask Maps is "now in 200+ countries". Google's post says it is expanding to 30
  more European countries and WILL then be in 200+. The long video says it correctly. Read "will" vs "is" carefully.
- Stock robot (landscape): good 1080p results for phones/laptops/cities. Bad: "busy city street people" (religious
  festival tag), "online shopping laptop" + "credit card payment phone" (cartoons), "phone settings" (a lake),
  "stopwatch timer" (digits fight a number graphic), "server room lights" (hacker clip), "tourists mountain view"
  (Crimea-tagged). The robot can return the SAME clip for a retry phrase that matches an earlier line: check tags.
- Scheduled-task changes need the owner's approval and cannot be made from a scheduled run: see channel/scheduled_tasks.md.
- Render: 2-CPU sandbox renders 1080p at ~0.5x real time (~10-15 min for 4.6 min). GitHub/Cloudinary 100 MB limit:
  make_long.py fits the file to 92 MB with 2-pass x264.

## 2026-11-20 Friday night run (video 011) + week 2 review
- vidIQ (YouTube Analytics, 23 Oct-20 Nov, 5 credits, 115 left): 1,887 views on 7 Shorts. FIRST SUBSCRIBER came from 007 Gemini 4 Hydrogen (Metricool YTEV01 = 1 on 18 and 19 Nov).
  007 (Slot A, shock-claim, 26.9 s): only 28 views so far but 9 engaged and avg 20 s = 74% viewed, the best retention yet next to 002 (69%). 008-010 not in YouTube Analytics yet (2-day lag).
- 007 breaks the "Slot A = 600+ views" pattern (A: 622, 775, 28). Topic matters more than slot: broad consumer apps (Instagram, Spotify/Reddit) took off, a model launch did not. Keep the slot test running; Monday run decides with 008 (B) and 009/010 (same-day A vs B).
- Short Shorts keep viewers: 26-28 s videos (002, 007) hold 69-74%; 28-36 s list/news ones sit at 41-46%. Aim for ~26-28 s and ~80 words.
- Metricool: 009 published as YouTube YYwW5bng7Zs, 010 as e44-PoG_oF8. Metricool per-video rows still empty.
- Video 011 (Google AI Mode temporary threads = incognito for AI search): Saturday AI-tip pillar with a `question` hook instead of `warning` (006 warning + how-to was worst at 26%), bf_emma, 28.0 s, 85 words, Slot A 16:00 PKT Sat 21 Nov.
- Engine: added `lock` and `pen` (dotted-border) icons.
- Stock robot: "woman reading phone" returned a Quran-reading clip (dropped: religious), "padlock security door" an AI earth render, "laptop keyboard closeup" an abstract light blur. "hand scrolling smartphone", "finger tapping phone screen", "woman laptop home", "young man smartphone" worked well.

## 2026-11-20 catch-up run (video 010, replaces missed Tue 17 Nov run)
- Video 010 (ChatGPT Live Dictation, free on every plan): `you-can-now` hook (2nd use), Wednesday pillar "free AI replaces a paid app", am_michael, 32.2 s, Slot B 04:00 PKT Fri 20 Nov (009 has Slot A 16:00 the same day: first same-day A vs B test).
- Added a `mic` icon to engine/render.py.
- Stock robot: "man speaking microphone" returned a dark party crowd; "student laptop library" an anime illustration; "friends laughing phone" no result. Stopwatch/hourglass and phone-keyboard phrases worked well.

## 2026-11-19 Thursday night run (video 009)
- 008 Google Maps published 19 Nov 04:00 PKT (YouTube BeTPYbFU6eA). Metricool shows the channel's FIRST subscriber on 18 Nov (YTEV01 = 1). Metricool per-video rows still empty; daily views rows stop after 15 Nov (2-3 day lag).
- vidIQ keyword check (5 credits, 120 left): "free ai tools" ~194K/month (IN 31%, PK 26%), "google ai pro free" ~155K (+56%, low competition 30), "gemini ai" ~120K, "gemini free" ~33K. Free-Google-AI wording is in demand: used "Now Free" in title + thumbnail.
- Video 009 (3 AI tools: Gemini Tasks free, Suno Visuals, Instagram content protection): `number` hook again (005 number = best video, 771 views), bm_george, 32.2 s, ~88 words, Slot A 16:00 PKT Fri 20 Nov.
  Hook leads with the strongest item ("Gemini's paid AI agent is now free") instead of "3 tools you missed" to fight the first-second swipe.
- Stock robot: "young man phone surprised" gave a woman on black, "tokyo city night" and "singer microphone studio" gave AI anime art, "person reading phone couch" a dark portrait, "woman using phone cafe" a woman in bed. "new york city aerial", "india city street" (Delhi metro), "woman headphones music", "woman filming smartphone" worked.

## 2026-11-18 Wednesday night run (video 008)
- No Tuesday-night run happened (17 Nov), so no Short goes out on Wed 18 Nov. 008 is for Thu 19 Nov.
- vidIQ (YouTube Analytics, 21 Oct-18 Nov, 5 credits, 125 left): 1,875 views on 6 Shorts, still 0 subscribers.
  Only 005 is still growing (669 -> 771 views, 80 engaged); the others are flat, so a Short gets almost all its views in the first 2-3 days.
  007 Gemini 4 Hydrogen (published 17 Nov 16:00, YouTube ebWuYbsB9yw) is not in YouTube Analytics yet (2-day lag).
- Metricool YouTube per-video analytics still empty; channel daily views now show (13 Nov 817, 11 Nov 646) but 0 subscribers.
- Video 008 (Google Maps Ask Maps trip planner): `question` hook (2nd use; 003 question = 627 views), bf_emma, 26.0 s, ~85 words, Slot B 04:00 PKT.
  This is the deciding Slot B test: if 008 is under 200 views by the Monday run, switch all posts to Slot A 16:00 PKT.
- Engine: added `pin` and `calendar` icons; thumbnail lines now shrink to fit the width ("MAPS NOW" in the 190 px font overflowed: M/W are wide).
  Voice: "countries", "territories", "iPhone", "Android" added to CUSTOM.
- Stock robot: "nail salon manicure" gave an abstract pink render, "hand holding smartphone street" a cartoon, "couple travel city map" an old map with country names,
  "hairdresser cutting hair" clippers with a brand logo, "friends eating cafe" no result. "dog grooming", "car mechanic garage", "airplane flying sky", aerial coastal road worked well.

## 2026-11-16 Monday night run (video 007)
- vidIQ (YouTube Analytics, 19 Oct-16 Nov, 5 credits, 130 left): 1,771 views on 6 Shorts, 0 subscribers.
  005 3 AI tools 669 (67 engaged, 47%), 003 Instagram 627 (38 engaged, 46%), 001 146, 006 CarPlay 132 (avg 7 s = 24.5%, worst), 004 120, 002 77.
- PATTERN (holds across all 5 slot-tested videos): Slot A 16:00 PKT beats Slot B 04:00 PKT by ~5x. A: 627, 669 views. B: 77, 120, 132.
  Keep the A/B alternation until the 4-week test ends as the strategy says, but if the next B video (008) is again under 200 views, switch all posts to 16:00 PKT.
- Early signal (not yet a pattern): the `warning` hook + how-to (006) lost viewers fastest (24.5%); `number` list and `question` hooks did best. Broad consumer apps (Instagram, Spotify/Reddit) beat niche ones (CarPlay).
- Engaged views are still only 6-10% of views: swipe-away in the first second is the main problem. 007 hook tested with a 10-word claim and on-screen headline from frame 1.
- Video 007 (Gemini 4 Hydrogen): `shock-claim`, am_michael, 26.9 s with ~74 words (shortest yet), Slot A. render.py stat scene now supports decimals (2.5x).
- Stock robot: "scoreboard stadium" gave an aerial city, "laptop screen code" had readable Unity code text, "coffee shop laptop" a cartoon. Dropped them via `clips`.

## 2026-11-13 Friday night run (video 006) + week 1 review
- vidIQ (YouTube Analytics, 16 Oct-13 Nov, 5 credits, 135 left): still only 001 and 002 have rows; 003-005 not in YouTube Analytics yet (about 2-day lag).
  001: 146 views, 13 engaged views, avg 15 s (41%). 002: 61 views (up from 38), 4 engaged views, avg 19 s (69%), 1 like. 0 subscribers.
- Engaged views are only ~7-9% of views: most viewers swipe away in the first seconds. The first frame + first sentence must work harder (big claim on screen at 0.1 s, strong moving shot).
- Metricool YouTube analytics still empty (only a 184-view row on 9 Nov). Keep using vidIQ.
- Video 006 (Gemini on Apple CarPlay): first `warning` hook ("Don't grab your phone in the car"), first Saturday "AI tip" pillar, bm_george, 28.6 s with ~83 words, Slot B 04:00 PKT. All 6 hook styles now used once.
- Render check: hook headline "Stop grabbing" (13 chars) overflowed in the big hook font; keep hook lines <= ~11 characters.
- Stock robot: "car touchscreen dashboard", "email inbox laptop", "phone car mount" gave no result; "calendar planner desk" gave a text card, "friends lunch restaurant" gave flowers. In-car driving shots (Peugeot interior, hands on wheel) worked well.

## 2026-11-12 night run (video 005)
- Metricool still returns 0 / no rows for YouTube analytics (4 Shorts published, 001 now 3+ days old). Rely on vidIQ channel analytics (Mon/Wed/Fri) for real numbers; Metricool YouTube stats look broken, not just slow.
- vidIQ keyword check (5 credits, 140 left): "ai tools" ~700K searches/month, "free ai tools" ~182K (best overall score 69, lower competition 46), "new ai tools" ~84K but falling (-32%). Top markets IN/PK/US. Put "AI tools" / "free AI tools" in titles and tags.
- Video 005: first `number` hook and first Friday "3 AI tools" list. 85 words at speed 1.08 gave 28.5 s (about 3 words per second for a list).
- Metricool accepted a custom videoThumbnailUrl for this Short (no VIDEO_THUMBNAIL_NOT_APPLICABLE error).
- Stock robot: "friends group photo" returned kids running in an alley, "woman closing eyes" an underwater fantasy image, "shopping bags" a text animation. Headphones/music and phone phrases worked well.

## 2026-11-12 - first real numbers (vidIQ / YouTube Analytics, 9-12 Nov)
- Channel: 707 total views across 4 Shorts in 3 days, 0 subscribers yet.
- 001 ChatGPT GIFs (36.6 s): 146 views, avg 15 s = 41% viewed.
- 002 Meta Muse (28.3 s): 38 views, avg 23 s = 79% viewed.
- Early signal (only 2 videos, NOT a pattern yet): the shorter video kept people far longer. Keep 25-30 s.

## 2026-11-11 night run (video 004)
- 003 published on time at 16:00 PKT (YouTube id djHqCYJHOPA). Metricool still returns no per-video rows and 0 channel totals for all 3 published Shorts (2+ days after 001). If still empty at the next run, check the YouTube connection in Metricool or ask the owner for Studio numbers.
- Video 004 (Claude Sheets/Whiteboards/Meetings): first `vs` hook ("Claude vs Excel?"), first Thursday "news of the week" pillar, voice am_michael, Slot B 04:00 PKT.
- Length: first render was 36.3 s with ~96 spoken words; cutting to ~85 words gave 31.7 s. Rule of thumb at speed 1.08: about 2.7 words per second, so aim for 70-90 words.
- Stock robot: "man looking at monitor" returned a statue, "sticky notes wall" music notes, "hand writing whiteboard" an ink bottle. Office/laptop/video-call phrases worked well.

## 2026-11-10 night run (video 003)
- Both 001 and 002 are published on YouTube (Metricool status PUBLISHED), but Metricool still returns no per-video rows and channel totals of 0. Its YouTube analytics seem to lag 1-2+ days; numbers to be filled in as soon as they show.
- Video 003 (Instagram Effect Builder): first `question` hook, voice bm_george, 31.1 s, Slot A 16:00 PKT (first Slot A test). Wednesday pillar "free AI replaces a paid app".
- Render check: a 2-line cta headline must stay under ~13 characters per line ("would you make?" overflowed; "What would / you make?" fits).
- Stock robot: "woman/girl selfie smartphone" twice returned a clip with a printed T-shirt slogan; "analog camera hands" returned a frog. Re-using a good clip from another scene via `clips` was faster than more retries.

## 2026-11-09 night run (video 002)
- Metricool has no per-video data yet for 001 (published 21:15 PKT, ~2 h before the check); channel totals 0. Retry tomorrow.
- Video 002 (Meta Muse Spaces): shortened to 28.3 s (001 was 36.6 s) per the 25-35 s rule; first Slot B (04:00 PKT) test; voice bf_emma; hook `shock-claim`.
- Render check: feature titles longer than ~18 characters overflow the frame width; keep feature `title` short (e.g. "Plan. Track. Play.").
- Stock robot: "concert crowd" returned a religious festival clip and "colorful design laptop" a text card; read the tag line in the stock output, not only the sheet.

## 2026-11-09 - launch
- Video 001 (ChatGPT Images 2.6 GIFs) scheduled 21:15 PKT, hook style `you-can-now`, voice am_michael, music Pulsar.
- Stock robot: Pixabay returns off-topic results for vague words; tag-relevance filter + blocklist added.
  Concrete visual phrases ("hand scrolling smartphone", "friends selfie phone") work best.
- No performance data yet. First pattern review after 5 videos.

## 2026-11-23 night run (video 012)
- Metricool daily views (YTEV02) now work: ~2,050 views 9-19 Nov (best days: 13 Nov 817, 11 Nov 646). Rows for 20-22 Nov are still empty (lag ~3 days). L001 (long video #1) is live: youtube id qb5gotN7gDk.
- Quiet news window (20-23 Nov): few consumer launches that are free + broad. The Gemini GIF maker (Omni 1.2 Flash, 8 countries, 18+) was skipped because Google's Help page says a Google AI plan is needed while news sites say free: unclear, so not used for "Free AI Tool".
- Video 012 = first "Free AI Tool #1" (series counter in state.json). An evergreen how-to (Gemini imports ChatGPT/Claude chats) that Google re-promoted on 19 Nov; framed as a tool, not as "new". number hook, am_michael, 69 words at 1.15 = 25.1 s (85 words = 30.1 s: ~2.75 words/s).
- Official images: blog.google images (storage.googleapis.com) are blocked by the session proxy but the stock robot fetches them fine (png and webp both worked).
- Engine fix: thumbnail.py crashed when scene 0's first clip is a still image (seeked 1.8 s into a PNG); now seeks 0 for images.

## 2026-11-24 night run (video 013)
- Metricool: daily views (YTEV02) filled up to 20 Nov only (17 Nov 31, 18 Nov 12, 19 Nov 125, 20 Nov 129); ~1 new subscriber a day 20-23 Nov (3 on 23 Nov).
- Video 013 = Wednesday "AI trick": Google Vids personal avatars now free for any personal Google account (Google blog 17 Nov). question hook, bf_emma, 74 words at 1.15 = 24.2 s.
- Official image lesson: Google's Vids hero image has a big centred text line ("Anyone can create a personal avatar in Google Vids"). As scene-0 clip it clashed with our headline AND showed through the thumbnail. Dropped it; frame 0 now a bright stock shot. Check official images for big text before using them as scene-0 / thumbnail background.
- News check 22-24 Nov: GPT-6.2 Sol in ChatGPT chat (paid only), ChatGPT Space for Plus (paid), AI Mode + Wallet/Drive (US-type rollout, not EU/UK): skipped as not free/global.
- Stock robot: "woman face closeup" gave lip-gloss makeup, "young woman portrait smiling" and "woman smiling laptop" gave anime AI art, "scanning qr code phone" no result, "smartphone camera hand" a cartoon. Re-used good clips via `clips` instead.

## 2026-11-25 growth analysis (Wed 02:10 PKT)
- vidIQ 28 Oct-24 Nov (10 credits, 90 left to 12 Dec): Shorts 001-011 = 2,314 views, 288 engaged (12%). Engaged % 001-006 ~9%,
  007-011 ~27% (pattern, 5 videos) but reach per new Short is only 13-150 views vs 622-777 for 003/005.
- L001 long video: 37 views, 20 engaged, 125 s avg (46%), 2 subs; its views came from "related/suggested" (152 s avg).
- Traffic: Shorts feed 88%, search 8%. 04:00 PKT Shorts (002/004/006/008) all < 135 views.
- Frame check: all first frames dark (mean 36-80/255). 010/011 (brand in kicker + first words) best engaged %; 013 hides the brand until ~4 s.
- Engine: render.py now lifts footage brightness/saturation and draws the scene-0 kicker as a big solid pill (tested on 013 preview frames).
- vidIQ shorts_stayed_to_watch needs the vidIQ browser extension (not connected); no credits were charged for the failed call.
