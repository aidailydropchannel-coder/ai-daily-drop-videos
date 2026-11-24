# AI Daily Drop: strategy and timetable

## Goal
Grow a faceless AI tools & tech news channel to the YouTube Partner Program as fast as possible, for free,
until the numbers show growth. Do not spend money on tools until the owner decides the channel is working.
YPP entry until 31 Jan 2027: 1,000 subscribers + 4,000 watch hours (12 months) or 10M Shorts views (90 days).
From 1 Feb 2027 new applicants need 8,000 watch hours (365 days) or 20M Shorts views (90 days).

## Target audience
- English-speaking viewers, 18-34, students and young professionals who use ChatGPT/Gemini/Claude and want free tools
  that save time or make money. Core regions: US, UK, Canada, Australia (highest ad rates) plus India/Pakistan/Philippines
  (huge AI-curious Shorts audiences).
- What they care about: "can I use this today, is it free, what does it do for me". Not deep technical detail.
- Write for a 16-year-old's vocabulary, a busy adult's patience.

## How the Shorts algorithm decides reach (research, Nov 2026)
- Every new Short is shown to a small test audience in the Shorts feed; reach widens only if those viewers watch
  instead of swiping, then it is shown to bigger groups. Subscriber count matters little.
- Signal 1: **viewed vs swiped away** (decided in the first 1-2 seconds). Benchmarks: 70%+ viewed = viral territory,
  ~50% average, under ~30% the Short dies.
- Signal 2: **average percentage viewed** (completion, re-watches count). 70%+ excellent, 50-70% gets pushed, under 30% stops.
- Then: shares, comments, likes, subscribing after watching.
- So: the first frame + first sentence are the whole game; shorter Shorts finish more often; endings that loop back
  into the start get re-watched.
- "Viewed vs swiped away" is only in YouTube Studio (not Metricool). Metricool gives views + average view duration ->
  use retention_pct = avg_view_s / length_s as our main quality score.

## Video rules that follow from this
- Length **25-35 s** (shorter than our first video's 36.6 s). 5-7 scenes.
- Frame 1: moving footage + the big claim on screen. Sentence 1: the payoff ("ChatGPT can now make GIFs"), never an intro.
- Pattern interrupts: a new shot every 2-3 s, flash + whoosh on cuts, captions word by word.
- Last line flows back into the first (loop) or asks a question that invites a comment.
- One topic, no filler. If a sentence can be cut without losing the point, cut it.

## Posting plan (free: Metricool free plan = 20 posts/month) - updated 22 Nov 2026
**4 Shorts (Tue-Fri) + 1 long video (Sunday) per week.** Shorts views do not count toward the 4,000 watch hours,
so the weekly long video is what moves us toward monetization.

| Day (PKT) | What | Made by | Goes live |
|---|---|---|---|
| Mon 23:34 | Short: Free AI Tool #N | nightly run | Tue 16:00 |
| Tue 23:34 | Short: ChatGPT/Gemini trick | nightly run | Wed 16:00 |
| Wed 23:34 | Short: 3 AI Tools You Missed #N | nightly run | Thu 16:00 |
| Thu 23:34 | Short: biggest AI news people use + **weekly report** | nightly run | Fri 16:00 |
| Sun 10:40 | **Long video: "AI News This Week" #N** (4-6 min, 3 thumbnail options) | weekly long-video task | Sun 21:00 |
| Wed + Sat night | growth analysis (vidIQ credits, fixes) | growth analysis task | - |

- 16:00 PKT for Shorts (the slot test is over: ~5x the views of 04:00).
- Sunday 21:00 PKT for the long video (= 16:00 UK / 11:00 New York / 21:30 India: Sunday is a high-viewing day for
  long-form; to be tested against performance once we have 4+ episodes).
- Monthly budget: ~17 Shorts + 4-5 long videos = 21-22 in long months. If the 20 are used, the long video gets the slot
  and the month's last Short is made + committed but uploaded by hand in YouTube Studio.
- Every thumbnail (long + Shorts) follows channel/thumbnail_playbook.md.

## Free tools only (current stack)
Claude (scripts, research, editing, analysis) - Kokoro voice (free, local) - Pixabay stock (free) - GitHub (free, robot +
storage) - Cloudinary free (archive) - Metricool free (20 scheduled posts/month + analytics).
If growth is proven later: Metricool Starter for daily posting, or a free YouTube Data API project once Google's free
compliance audit is approved (unaudited API uploads are locked to private, so it cannot be used before that).

## Growth levers to test (record results in learnings.md)
- Hook styles: shock-claim, question, you-can-now, number, vs, warning.
- Topics: ChatGPT/Gemini/Claude features vs new startup tools vs phones/hardware vs money stories.
- Voices: 3 rotating; if one clearly wins over 10+ videos, use it more.
- Length: 25 s vs 35 s.
- Later: one 6-10 min long video per week (watch hours for YPP); cross-post the same Shorts to TikTok/Instagram
  through Metricool (counts against the same 20 posts, so only once there is room).

## Update 2026-11-21 (after weeks 1-2: ~1,900 views, 1 subscriber, only 6-10% engaged views)
- Diagnosis: viewers swipe in the first second (empty/blurry first frame, headline faded in, generic stock footage that
  did not show the product, niche topics). Fixed: instant headline at frame 0, official product images allowed,
  voice 1.15x, 25-28 s, every Short at 16:00 PKT, broad topics.
- Series for a reason to subscribe: number recurring formats in titles/thumbnails, e.g. "Free AI Tool #7",
  "3 AI Tools You Missed #4". Keep the series names consistent.
- Weekly plan (4 Shorts + 1 long video, inside Metricool's 20 free posts):
  Tue: Free AI Tool #N | Wed: ChatGPT/Gemini trick | Thu: 3 AI Tools You Missed #N | Fri: biggest AI news people use |
  Sun: long video "AI News This Week".
- The growth analysis task (Wed + Sat nights) reviews this plan every few days and may change it based on data.

## Update 2026-11-25 (growth analysis: ~2,350 views, ~11 subs)
- Biggest problem now: reach. Engaged views rose to ~27% but new Shorts stall at 13-150 views (avg viewed 38-52%).
- First second: brand name in a big scene-0 pill + in the first spoken words; bright scene-0 footage (engine now lifts
  brightness/saturation). End CTA names the next numbered episode.
- Funnel: Shorts -> weekly long video (watch hours + 2 subs from 37 views on L001). Owner can link each Short to the latest
  long video with YouTube's "Related video" field (Studio only; Metricool cannot).
