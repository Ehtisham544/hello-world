# SIC long videos — runbook for each scheduled run (Wednesday & Sunday)

Channel: **Scholarships in China (SIC)**, channel ID `UC2SR24QYqYCaqp8wBYR70Qw`. The owner (SHAM) gave full control: do NOT ask him anything. ONE long video (16:9, 8–10 min) per run.

## 0. Setup
Attach repo `Ehtisham544/hello-world` (add_repo, access `push`), clone `git clone --depth 1 https://github.com/Ehtisham544/hello-world /home/claude/hello-world`. Read `long/long_topics.md`.

## 1. Pick the topic
Take the FIRST row in `long/long_topics.md` with status `todo` (or `ready` = already rendered and hosted: skip to step 5 and use the file/thumbnail URLs written in that row).

## 2. Research
Use official sources (campuschina.org, studyinchina.csc.edu.cn, university admission pages, Chinese embassy/consulate notices, provincial government pages) plus https://cscguideofficials.com/ for leads. Only state facts confirmed in a source fetched this run. Never invent deadlines, agency numbers, amounts. Audience: students from all countries, English.
Standard Chinese Government Scholarship stipends (OK to state): Bachelor CNY 2,500 / Master 3,000 / PhD 3,500 per month.

## 3. Write the spec — copy the structure of `long/example_long_spec.json`
`{"title": ..., "thumb": {"tag","big","line1","line2","emo"}, "slides": [...]}`
- Slide kinds: `intro` (title, sub, 2–3 items voice only), `chapter` (num "01".., title, 1 short item), `list` (chapter label like "STEP 2 · PROFESSOR", title, 3–6 items each with `say`, `b`, `emo`), `outro` (title, sub, 2–3 items).
- Target ≈ 1,250–1,450 spoken words total (≈ 8–10 min). 8–10 chapters.
- `say`: natural spoken English, 1–3 sentences; spell out numbers; space acronyms ("C S C", "P H D", "H S K"); URLs spoken ("campus china dot org").
- `b`: bullet ≤ 42 characters, one `*gold*` phrase. `emo`: one common emoji.
- Thumb: `big` ≤ 9 chars (e.g. "CSC 2027", "TOP 10"), `line1`/`line2` ≤ 13 chars each, ALL CAPS.
- Intro: hook in the first sentence + promise of the video + "save this video".
- Outro: recap + "Every day on this channel we share a new fully funded scholarship… subscribe" + ask for comments.

## 4. Render
```
cd /home/claude/hello-world/long
LSPEC=/home/claude/long_spec.json OUT=/home/claude/long.mp4 THUMB=/home/claude/thumb.jpg bash make_long.sh
```
Prints chapter timestamps at the end (also `long/chapters.txt`). Check 3 frames (`ffmpeg -ss T -i /home/claude/long.mp4 -frames:v 1 f.png`, Read them): no overflowing text. Check the thumbnail image too.

## 5. Host (public links) on branch `long-videos` (keep only the newest files)
```
rm -rf /tmp/lv && mkdir /tmp/lv && cd /tmp/lv && git init -q && git checkout -q -b long-videos
cp /home/claude/long.mp4 sic-long-NNN-slug.mp4 && cp /home/claude/thumb.jpg sic-long-NNN-thumb.jpg
git add . && git -c user.name=Claude -c user.email=noreply@anthropic.com commit -qm "long NNN"
git remote add origin https://github.com/Ehtisham544/hello-world && git push -f origin long-videos
```
URLs: `https://raw.githubusercontent.com/Ehtisham544/hello-world/long-videos/<file>` (verify 200 with `curl -sI`).

## 6. Post — Zapier YouTube `upload_video` (selected_api `YouTubeV4CLIAPI`, tool_name `youtube_upload_video`)
`title` (≤100 chars, keyword-first, e.g. "CSC Scholarship 2027: How to Apply STEP BY STEP (Fully Funded)"), `description` (2-line summary, chapter timestamps, official links, "Subscribe to Scholarships in China (SIC)…", 6–8 hashtags), `video` = mp4 URL, `thumbnail` = jpg URL, `privacy_status` "public", `category_id` "27", `made_for_kids` "false", `default_language` "en", `default_audio_language` "en", `notify_subscribers` "true", `tags` 10–15.
If the upload fails only because of the thumbnail, retry once without `thumbnail` and mention it in the report. Confirm `channelId` = `UC2SR24QYqYCaqp8wBYR70Qw`.

## 6b. Starter comment
Post a top-level comment inviting questions (same API call as in `sic/RUNBOOK.md` step 5b). Each long video must be new content, with a different hook, title style and thumbnail wording from previous long videos.

## 7. Log
In `long/long_topics.md` set the row's status to `posted` with date + video link; commit to `main` and push (`git -c push.negotiate=true push origin main`). If the queue has fewer than 3 `todo` rows, append new useful topics (no duplicates).

## 8. Report
One short message to SHAM: title + YouTube link (or exactly what failed). Never post an unverified or broken video.
