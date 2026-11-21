# SIC Shorts — runbook for each scheduled run

Channel: **Scholarships in China (SIC)** — @scholarshipsinchina-sic — channel ID `UC2SR24QYqYCaqp8wBYR70Qw`.
Owner (SHAM) gave full control: research, script, render and post **without asking**. Make exactly ONE Short per run.

## 0. Setup
1. Attach the repo (add_repo owner `Ehtisham544`, repo `hello-world`, access `push`) and clone:
   `git clone --depth 1 https://github.com/Ehtisham544/hello-world /home/claude/hello-world`
2. Read `sic/posted.md` (log of everything already posted). Never repeat a university/scholarship posted in the last 60 days, and never repeat a tips topic.

## 1. Pick the topic (by slot, from the prompt)
- FIRST read `CONTENT_POOL.md` (repo root) and follow its rotation rules — the channel covers ALL funded opportunities in China, not only CSC.
- **Slot A (morning) and Slot B (afternoon):** one funded opportunity from the pool (categories 1–10 and 12): CSC tracks, provincial/city scholarships, university scholarships, Confucius Institute, MOFCOM, elite programs (Schwarzman, Yenching…), interesting programs, fellowships, postdocs, careers/jobs after a PhD. A and B on the same day must be different categories.
  Source ideas: https://cscguideofficials.com/ (latest posts), then VERIFY on the official university admission page or campuschina.org / studyinchina.csc.edu.cn.
  Prefer scholarships whose deadline is still open. Prefer well-known universities.
- **Slot C (evening):** a practical how-to / tips Short for scholarship applicants, rotating topics, e.g.: how to email a Chinese professor for an acceptance letter; CSC documents checklist; study plan tips; recommendation letters; Type A vs Type B; how to find your agency number; physical exam form; police certificate; common mistakes that get CSC applications rejected; IELTS vs HSK requirements; stipend amounts by level; best months to apply; how to pick universities; life on a CSC scholarship.
- Only state facts you confirmed in a source fetched this run. Standard Chinese Government Scholarship stipends may be stated for CSC programs: Bachelor CNY 2,500, Master CNY 3,000, PhD CNY 3,500 per month. Never invent deadlines, agency numbers or amounts — if unconfirmed, leave them out.
- Audience is students from ALL countries (not only Pakistan). English.

## 1b. Keep every video fresh (owner's rule: every video must be NEW, different content)
- Different scholarship/university/topic from everything in `sic/posted.md` (60 days for scholarships, never for tips).
- Vary the HOOK style every time and never reuse a hook from the last 15 rows of posted.md. Rotate styles: question ("What if…?"), shocking fact ("This university pays you ¥3,500 a month"), urgency ("Deadline in 30 days!"), myth-buster ("You DON'T need an agent"), countdown ("3 things…"), "Stop scrolling if you want to study in China…".
- Vary title wording and the order/angle of facts (eligibility-first, money-first, steps-first, deadline-first). Vary emojis.

## 2. Write the spec (JSON) — see `sic/example_spec.json`
`{"header": "...", "beats": [ {"say": ..., "cap": ..., "emo": ...}, ... ]}`
- `header`: topic pill, UPPERCASE, max ~28 chars, e.g. `"WUHAN UNIVERSITY  ·  CSC 2027"` or `"CSC TIPS"`.
- 14–19 beats, total voice ≈ 45–58 s. Beat 1 = scroll-stopping hook (question / bold promise). Last two beats: "Save this and send it to a friend who needs it." and "Follow for a new fully funded scholarship every day."
- `say`: spoken text. Spell out numbers ("three thousand five hundred"), space acronyms ("C S C", "P H D", "H S K"), keep each beat 1 short sentence.
- `cap`: on-screen text, max 3 lines (use `\n`), max ~18 characters per line, wrap ONE key phrase per beat in `*stars*` (gold).
- `emo`: one common emoji per beat (🎓🌍💸✅🏠🏥🤔📊📝⏰🔖🔔1️⃣2️⃣3️⃣📧📄✈️🇨🇳 etc.).
- Optional money counter beat: `"cap": "+ *¥{n}*\nevery month", "count": 3500`.

## Real-footage backgrounds (media library)
Each beat/slide automatically gets a matching real background video/photo from `media/` (tags: students, study, exam, campus, city, china, graduation, documents, money) chosen from its text. To force one, add `"bg": "<tag>"` to a beat (Shorts) or to a slide/item (long videos), e.g. `"bg": "money"` for stipend lines, `"documents"` for document lists, `"graduation"` for wins/CTA, `"city"`/`"china"` for places, `"campus"` for universities. Use a variety of tags across the video.

## 3. Render
```
cd /home/claude/hello-world/sic
SPEC=/home/claude/spec.json OUT=/home/claude/short.mp4 bash make_short.sh
```
(~3–5 min; downloads voice model from GitHub on first run.) Then check 2 frames, e.g.
`ffmpeg -ss 3 -i /home/claude/short.mp4 -frames:v 1 /home/claude/f1.png` and one near the middle; Read them. If any caption overflows or is cut, shorten it and re-render.

## 4. Host the file (public link for YouTube)
Name: `sic-NNN-slug.mp4` (NNN = next number from posted.md).
```
rm -rf /tmp/vids && mkdir /tmp/vids && cd /tmp/vids && git init -q && git checkout -q -b videos
cp /home/claude/short.mp4 sic-NNN-slug.mp4 && git add . && git -c user.name=Claude -c user.email=noreply@anthropic.com commit -qm "video sic-NNN"
git remote add origin https://github.com/Ehtisham544/hello-world && git push -f origin videos
```
URL: `https://raw.githubusercontent.com/Ehtisham544/hello-world/videos/sic-NNN-slug.mp4` (check with `curl -sI` → 200).

## 5. Post with Zapier → YouTube `upload_video` (selected_api `YouTubeV4CLIAPI`, tool_name `youtube_upload_video`)
params: `title` (catchy, ≤100 chars, ends with `#shorts`), `description` (what it covers, eligibility, steps, official links, deadline, "Follow Scholarships in China (SIC)…", 6–8 hashtags), `video` (the raw URL), `privacy_status` "public", `category_id` "27", `made_for_kids` "false", `default_language` "en", `default_audio_language` "en", `notify_subscribers` "true", `tags` (6–10).
Confirm the result's `channelId` is `UC2SR24QYqYCaqp8wBYR70Qw`.

## 5b. Starter comment
Post one top-level comment on the new video inviting questions (Zapier `youtube_make_api_mutating_request`, method POST, url `https://www.googleapis.com/youtube/v3/commentThreads`, querystring `{"part":"snippet"}`, header Content-Type application/json, body `{"snippet":{"channelId":"UC2SR24QYqYCaqp8wBYR70Qw","videoId":"ID","topLevelComment":{"snippet":{"textOriginal":"…"}}}}`). Vary the wording; include the key deadline if known.

## 6. Log
Append to `sic/posted.md`: `| NNN | date | slot | [cat N] topic | video id | https://youtube.com/shorts/ID |` and add the hook text at the end of the topic cell as `(hook: …)`, commit to `main` and push (`git -c push.negotiate=true push origin main`).

## 7. Report
Send the owner one short message: topic + YouTube link. If something failed (render, upload, auth), say exactly what and stop — never post a broken or unverified video.
