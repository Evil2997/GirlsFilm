# Solution — Date Night Assistant

## Task

> Every Friday I go on dates with a new girl. Build an application using Claude that, via a console command, scans her Instagram, picks a series for the evening based on her likely interests, and finds it on a streaming service (Netflix, HBO, Prime) — I have subscriptions to the first two. Demonstrate prompts, skills, code and application architecture.

---

## What I Built

A CLI tool that runs as a single command:

```bash
python main.py --username <instagram_username>
```

The pipeline:

1. **Instagram** — authenticates via a saved browser session (Chrome/Firefox), scrapes the public profile: bio, hashtags from recent posts, captions, follower count
2. **Claude Opus 4.5** — receives the profile data, infers interests, and returns a structured JSON recommendation (series title, genre, reason, Russian translation)
3. **TMDB API** — searches for the recommended title, checks streaming availability by region (DE → US → GB), returns a direct search link on Netflix or HBO Max

---

## Key Decisions

**Why Instaloader over the official Instagram API?**
The official API requires app review and only works with your own account's data. Instaloader scrapes public profiles directly — which is exactly what this use case needs.

**Why browser session only?**
Instagram doesn't trust sessions created via terminal login — they get silently blocked. The only reliable method is importing cookies from a logged-in browser via `instaloader --load-cookies chrome`.

**Why structured JSON from Claude?**
The output needs to be machine-readable to pass into the streaming search step. The prompt instructs Claude to respond strictly in JSON, which is then validated with a Pydantic model. No regex parsing, no fragile string splitting.

**Caching**
Profile data is cached for 24 hours, Claude responses for 7 days (invalidated on profile or prompt change via MD5 hashing). This avoids unnecessary API calls on repeated runs for the same person.

**SQLite history**
Every recommendation is saved to a local database. Accessible via `--history` flag — useful for not recommending the same thing twice.

---

## Prompts

The prompt passes the following profile fields to Claude:

- Full name
- Bio
- Post count + follower count
- Hashtags from the last 12 posts (up to 20 unique)
- Captions from the last 5 posts (first 100 chars each)

Claude is instructed to:
1. Infer the person's interests from the data
2. Recommend one series or film ideal for a date night
3. Explain why it fits (2–3 sentences)
4. Respond strictly in JSON matching the `Recommendation` schema

---

## Architecture

```
CLI (argparse)
    ↓
session.py       — browser cookie import via Instaloader
    ↓
instagram.py     — profile scraping (bio, hashtags, captions)
    ↓
claude_client.py — structured recommendation via Claude API
    ↓
streaming.py     — TMDB title search + provider lookup by region
    ↓
Console output + SQLite history
```

---

## Stack

- Python 3.12
- Anthropic Claude API (`claude-opus-4-5`)
- Instaloader + browser-cookie3
- TMDB API
- Pydantic + pydantic-settings
- SQLite
- uv