# Thumbnail playbook (AI Daily Drop)

Written 22 Nov 2026 from 2025-2026 studies, YouTube's own docs, and a vidIQ look at this month's top AI-news and
AI-tools long videos. Follow it for EVERY thumbnail: long videos (1280x720) and Shorts covers (1080x1920).
Q = data study (correlation, not proof), P = YouTube platform fact, O = expert opinion.

## The 12 rules
1. **Watch time decides, not clicks alone (P).** YouTube's Test & Compare picks the winner by watch-time share, not CTR.
   The promise on the thumbnail must be paid off in the first 30 s of the video. No fake claims, ever.
2. **2-4 big words, max ~20 characters on the image (Q).** 4-6-word overlays had the biggest winner/loser gap (Eden,
   507k videos, Aug 2026); the median breakout had 5 words (vidIQ, 500 breakouts, Jul 2026); text-heavy thumbnails
   lost views (1of10, 300k videos, Feb 2026). News needs some text for context, so we use 2-4 words.
3. **The thumbnail adds to the title, never repeats it (Q+O).** Title = what it is (keyword first). Thumbnail = the
   feeling / the hook ("NOW FREE", "IT CALLS FOR YOU"). Copying the title word for word is more common in losers (Eden).
4. **One focal subject that passes the 0.5-second glance test (O).** One big thing: a product image, a bold icon,
   a giant number. At most 1-2 arrows / circles / badges (Eden: small positive edge; vidIQ: no more than 2).
5. **High contrast replaces a face (Q).** 89% of breakouts had a face, high contrast, or both (vidIQ). Faces add little
   below ~200k subscribers (1of10). We are faceless: use extreme contrast, glow and a bright subject instead.
6. **Bright, saturated, cyan-led colour (Q).** Mostly-cyan thumbnails got ~36% more views than average; dark thumbnails
   under-perform (1of10). Our navy is a frame or panel only; the subject and text must be bright. Add ONE hot accent
   (yellow #FFC43D) for the single most important word. Avoid large areas of YouTube red, pure white or pure black (O, vidIQ).
7. **Readable at phone size (P+O).** Suggested-video thumbnails are ~168x94 px. Always check a 320x180 and 168x94 copy:
   every word must still read. Heavy sans font (Inter Display Black), thick dark outline/shadow or a solid block behind text.
8. **Keep corners clear (O).** Bottom-right ~200x90 px (at 1280x720) is covered by the duration stamp; top-right holds
   hover icons; keep ~5% padding. Put the logo small, top-left.
9. **No raw screenshots (Q).** Plain screenshots are more common in losers (Eden). Show a product/press image cropped
   big inside a designed layout, never a whole UI screen.
10. **Curiosity gap that is TRUE (O, all top creators).** Show the outcome and leave the "how/which" for the video
    ("GEMINI'S AGENT IS NOW FREE" - which agent? where? how?). Never imply something the video does not show.
11. **Big numbers / money / FREE work in our niche (vidIQ niche scan, Nov 2026).** This month's AI-tools breakouts lean
    on FREE, a big number ("100", "5", "$0"), and a product hero. Use a number only when it is real and in the video.
12. **Upload big, test 3 variants (P).** Upload 1280x720+ JPG (<2 MB). For long videos, upload 3 clearly different
    options to Test & Compare in YouTube Studio when available (needs Studio on desktop; Metricool can only set one).

## What the top AI-news / AI-tools videos do right now (vidIQ outliers, Nov 2026, 15 credits)
- Weekly AI news leaders (Matt Wolfe, Paul J Lipsky, AI Search, WorldofAI): one central subject + floating product icons
  + 2-3 huge words ("AI NEWS", "Wild AI Week", "huge AI news"). Bright purple/blue/cyan glow backgrounds.
- Breakouts from small channels (4-11x their average): "FREE AND UNLIMITED", "100 VIDEOS PER DAY / COMPLETELY FREE",
  "5 AI TOOLS NOBODY IS TALKING ABOUT": a big benefit word in yellow/white, one hero, glowing dark-teal or blue background.
- Thumbnail swaps that doubled views (vidIQ title/thumbnail wins): busy UI screens were replaced by a big product logo
  + 2-3 words ("WORTH IT?", "ALMOST 2X", "GPT 6 EXPLAINED"). Shorter text, bigger subject, stronger colour.
- We do NOT copy any of these designs; we use the patterns: few words, one hero, bright glow, a benefit or a number.

## Our template (engine/thumbnail_long.py)
- 1280x720. Left 55%: 2-3 lines of text (Inter Display Black, white + one cyan or yellow accent line, thick outline).
  Right 45%: one hero (official product image in a glowing rounded frame, or a giant icon / number).
- Small logo + "AI DAILY DROP" top-left. Optional short badge (NEW / FREE / EP 1). Nothing in the bottom-right corner.
- Make 3 options (different hook words / different hero), look at each at full size AND at 320x180 and 168x94,
  pick the strongest, keep all 3 in the video folder (thumb_A/B/C.jpg, chosen one copied to thumb.jpg).
- Shorts covers (engine/thumbnail.py) follow rules 2-8 and 10 too: 2-3 lines, max ~12 characters each, centred in the
  middle 4:5 band (home feed crops vertical covers to 4:5).

## Sources
- YouTube Help, "A/B test titles and thumbnails" (support.google.com/youtube/answer/16391400); Social Media Today, 14 Jul 2025.
- YouTube Help, "Add video thumbnails" (support.google.com/youtube/answer/72431).
- Eden, "What makes a good YouTube thumbnail" (507,478 videos), 21 Aug 2026 - eden.so/blog/what-makes-a-good-youtube-thumbnail/
- vidIQ, "YouTube thumbnail study" (500 breakouts), Jul 2026 - vidiq.com/research/youtube-thumbnail-study/
- vidIQ, "YouTube thumbnail design tips", 14 Jul 2026 - vidiq.com/blog/post/youtube-thumbnail-design-tips/
- 1of10, "What actually makes a YouTube video go viral" (300k+ videos), 6 Feb 2026; "Thumbnail Trends 2026", 19 Jun 2026.
- Search Engine Journal on the 1of10 face study, 22 Dec 2025.
- Thumbcrafted, "YouTube thumbnail safe zones", 11 Apr 2026 (size estimates, unofficial).
- Tubefilter, Neal Mohan on TV as #1 US screen, 11 Feb 2025.
- vidIQ MCP (22 Nov 2026): outliers "AI news this week" + "new AI tools" (long, 3 months), title/thumbnail wins "AI tools and AI news".
