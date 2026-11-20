# SIC comment replies — runbook (runs every 3 hours)

Channel ID `UC2SR24QYqYCaqp8wBYR70Qw`. Owner SHAM gave full control: reply without asking him. All calls go through Zapier YouTube (selected_api `YouTubeV4CLIAPI`).

## 1. Fetch recent comments
`execute_zapier_read_action` tool_name `youtube_make_api_get_request`, action `_zap_raw_request`, params:
`{"fail_on_errors":"false","method":"GET","url":"https://www.googleapis.com/youtube/v3/commentThreads","querystring":{"part":"snippet,replies","allThreadsRelatedToChannelId":"UC2SR24QYqYCaqp8wBYR70Qw","maxResults":"100","order":"time"}}`
If a thread has `totalReplyCount` larger than the replies shown, fetch all replies with GET `https://www.googleapis.com/youtube/v3/comments` querystring `{"part":"snippet","parentId":"THREAD_ID","maxResults":"100"}`.

## 2. Decide what needs a reply
A thread needs a reply when the newest message in it is from someone else (author channel id ≠ `UC2SR24QYqYCaqp8wBYR70Qw`), i.e. a new top-level comment with no reply from us, or a follow-up after our last reply.
Skip: spam, scams, links/self-promotion, abuse, pure emoji or "nice" comments older than 24 h (for fresh short praise, a quick warm "Thank you! 🙏 Follow for daily scholarships" is fine).
To see what the video was about, look up its title/description (GET `https://www.googleapis.com/youtube/v3/videos` querystring `{"part":"snippet","id":"VIDEO_ID"}`) and `sic/posted.md` / `long/long_topics.md` in the repo if useful.

## 3. Write the reply
- Friendly, encouraging, specific, short (1–4 sentences, ≤ 600 characters). Answer the actual question.
- Accuracy first: if the question needs a fact (deadline, agency number, requirement), check an official source with web search/fetch before answering. If unsure, point them to the official page (campuschina.org, studyinchina.csc.edu.cn, the university's international admissions site, or their Chinese embassy) — never guess.
- Never promise admission or a scholarship. Never ask for money, documents, passwords, phone numbers or private contact. Remind people that applying is free and they should not pay agents.
- Reply in the commenter's language when you can (English default).
- Where natural, invite them to the long guide on the channel or to follow for daily scholarships — not in every reply.

## 4. Post the reply
`execute_zapier_write_action` tool_name `youtube_make_api_mutating_request`, action `_zap_raw_request`, params:
`{"fail_on_errors":"false","method":"POST","url":"https://www.googleapis.com/youtube/v3/comments","querystring":{"part":"snippet"},"headers":{"Content-Type":"application/json"},"body":"{\"snippet\":{\"parentId\":\"THREAD_ID\",\"textOriginal\":\"REPLY TEXT\"}}"}`
(JSON-escape the reply text.) Check status 200.

## 5. Report
If you replied to anything, finish with one line: how many replies and any question that needs SHAM personally (e.g. collaboration requests, complaints). If nothing needed a reply, just finish quietly.
