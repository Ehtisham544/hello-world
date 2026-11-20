# SIC daily community post — runbook

YouTube's API does NOT allow apps to publish community posts, so each day you PREPARE a ready-to-post community post and send it to the owner SHAM, who posts it from the YouTube app (Create → Post) in ~30 seconds. Do not ask him anything; just deliver it.

## 1. Setup
Attach repo `Ehtisham544/hello-world` (add_repo, access `push`), clone `git clone --depth 1 https://github.com/Ehtisham544/hello-world /home/claude/hello-world`. Read `community/posted_community.md`, `sic/posted.md` (recent Shorts) and `long/long_topics.md`.

## 2. Choose today's post type
Read `CONTENT_POOL.md` (repo root) — feature different categories of opportunities (not only CSC) across the week.
 (rotate; never the same type two days in a row)
1. **Poll** (best engagement): question + 2–4 options, e.g. "Which degree are you applying for in 2027? Bachelor's / Master's / PhD / Chinese language".
2. **Deadline alert**: one real, open scholarship deadline (verified on the official page this run) + image card.
3. **Quick tip**: one practical application tip + image card.
4. **Quiz poll**: a fact question with options (e.g. "What's the PhD stipend under CSC? ¥2,500 / ¥3,000 / ¥3,500") — answer in a reply/next day.
5. **Question to the audience**: "Which country are you from? Comment below 👇" / "What's your biggest problem with the CSC application?"
6. **Promote the newest long video** (on the day after a long video is posted): 2 lines + link.
Never repeat a post from `community/posted_community.md`. Facts must be verified on official sources this run.

## 3. Make the image (for types 2, 3, 6; optional otherwise)
`python3 community/card.py /home/claude/post.png "TAG" "Title line\n*gold words*" "small line 1\nsmall line 2" "EMOJI"` — TAG ≤ 18 chars, title ≤ 2 lines (~18 chars each). Read the PNG to check it.

## 4. Deliver to SHAM
Send ONE message (SendUserMessage) titled "📢 Today's community post — ready to copy", containing: the post text (≤ 5 short lines, 2–3 hashtags, emojis), poll options if any, and "How: YouTube app → Create (+) → Post → paste text / add image or poll → Post". Then send the image with SendUserFile (status proactive) if there is one.

## 5. Log
Append `| date | type | summary |` to `community/posted_community.md`, commit to `main`, push (`git -c push.negotiate=true push origin main`).
