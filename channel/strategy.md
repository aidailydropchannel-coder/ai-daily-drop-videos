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

## Posting plan (free: Metricool free plan = 20 posts/month)
- **5 Shorts per week, Tuesday to Saturday** (about 21/month; the run skips a day if the month's 20 are used).
  Big 2026 studies agree Thursday-Saturday are the strongest days for Shorts; Metricool's own study found more uploads
  do not automatically mean faster growth, so 5 strong videos beat 7 rushed ones.
- Production runs Mon-Fri at 23:34 PKT (night only - the owner uses Claude in the day). Each run makes tomorrow's Short.
- Two time slots under test on the posting day (Asia/Karachi):
  - **Slot B 04:00 PKT** (= 6 PM New York / 3 PM Los Angeles, the US evening window most studies favour for Shorts)
  - **Slot A 16:00 PKT** (Metricool's YouTube activity peak; = Europe afternoon, Asia evening, US early morning)
  - Alternate A/B by video number (odd = A, even = B) for the first 4 weeks, then use the winner from performance.csv.

| Day | Pillar | Example |
|---|---|---|
| Tue | New AI tool you can use today | "This free AI turns photos into 3D" |
| Wed | Free AI that replaces a paid app | "Stop paying for Canva: try this" |
| Thu | Biggest AI news of the week, explained simply | "OpenAI just raised $11B" |
| Fri | 3 AI tools you didn't know | quick-fire list, 3 tools in 30 s |
| Sat | AI tip / how-to (made by the Friday-night run, which also writes the weekly report) | "Make ChatGPT write like you" |

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
