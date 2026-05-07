# 💘 Date Night Assistant

An AI-powered CLI tool that:

1. Scans a public Instagram profile
2. Analyses interests using the Claude API
3. Recommends a series or film for a date night
4. Checks availability on Netflix / HBO Max / Prime Video via the TMDB API

---

## 🚀 Features

- Instagram parsing via Instaloader (Chrome / Firefox session)
- Claude Opus 4.5 — interest analysis and recommendation generation
- TMDB API — streaming provider lookup by region
- Direct search links to Netflix / HBO Max / Prime Video
- File-based cache for profiles (24h TTL) and LLM responses (7-day TTL)
- Recommendation history stored in SQLite
- CLI with verbose mode and `--no-cache` flag

---

## 🏗 Architecture

```text
CLI (argparse)
    ↓
session.py       — Instagram auth via Chrome/Firefox cookies
    ↓
instagram.py     — profile scraping via Instaloader
    ↓
claude_client.py — interest analysis, series recommendation
    ↓
streaming.py     — provider lookup via TMDB API
    ↓
Console output + SQLite history
```

---

## 📦 Project Structure

```text
GirlsFilm/
├── main.py
├── app/
│   ├── cli.py
│   ├── config.py
│   ├── models.py
│   ├── logger.py
│   ├── session.py
│   ├── instagram.py
│   ├── claude_client.py
│   ├── prompts.py
│   ├── streaming.py
│   ├── cache.py
│   └── database.py
├── cache/
│   ├── profiles/
│   └── llm/
├── history.db
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## ⚙️ Installation

```bash
git clone <repo>
cd GirlsFilm
uv sync
```

---

## 🔑 Environment Setup

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_claude_key
TMDB_API_KEY_2=your_tmdb_key
INSTAGRAM_USER=your_instagram_username
```

Get a TMDB API key: https://www.themoviedb.org/settings/api

---

## 🔐 Instagram Session

The app uses a browser session. Before the first run:

```bash
instaloader --load-cookies chrome
```

or Firefox:

```bash
instaloader --load-cookies firefox
```

The session is saved to `~/.config/instaloader/` and reused automatically on subsequent runs.

> **Note:** Only public Instagram profiles are supported. Terminal login via password is not supported — Instagram does not trust such sessions.

---

## ▶️ Usage

```bash
# Basic run
python main.py --username some_username

# Verbose mode
python main.py --username some_username -v

# Skip cache (force re-fetch from Instagram and Claude)
python main.py --username some_username --no-cache

# Show recommendation history
python main.py --username some_username --history
```

---

## 📋 Example Output

```text
💘 Date Night Assistant
========================================
📱 Establishing Instagram session...
Session valid — logged in as @your_account
🔍 Scanning profile @some_username...
🤖 Analysing interests with Claude...
🔍 Searching 'Physical: 100' on Netflix and HBO...

========================================
🎬 TONIGHT'S RECOMMENDATION
========================================

📺 Series : Physical: 100

🎭 Genre  : Reality Competition

💡 Interests of @some_username:
   • fitness / gymnastics
   • stretching / flexibility
   • beach / travel
   • medicine / healthcare

❤️  Why it fits:
   This Korean show perfectly combines a passion for sport and athleticism...

📡 Where to watch:
   ✅ Netflix — https://www.netflix.com/search?q=Physical+100

🎞️  TMDB: https://www.themoviedb.org/tv/210905
========================================
🌙 Enjoy your evening! 🍷
```

---

## 💾 Caching

| Type | TTL | Invalidation |
|------|-----|--------------|
| Instagram profile | 24 hours | on TTL expiry |
| Claude response | 7 days | on profile or prompt change |

---

## ⚠️ Known Limitations

- Only public Instagram profiles are supported
- Instagram rate-limiting: a 429 error may occur after frequent requests — wait ~30 minutes before retrying
- Streaming availability depends on region (priority: DE → US → GB)
- Instaloader 4.15.1 has an unstable GraphQL endpoint — the code includes a fallback via the iPhone API

---

## 🛠 Tech Stack

- Python 3.12
- Anthropic Claude API (`claude-opus-4-5`)
- Instaloader + browser-cookie3
- TMDB API
- Pydantic + pydantic-settings
- SQLite
- argparse
- uv