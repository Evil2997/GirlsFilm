# 💘 Date Night Assistant

AI CLI-приложение, которое:

1. Сканирует Instagram профиль
2. Анализирует интересы через Claude API
3. Рекомендует сериал или фильм для свидания
4. Проверяет доступность на Netflix / HBO Max / Prime Video через TMDB API

---

# 🚀 Возможности

- Instagram parsing через Instaloader
- Claude Opus 4.5 integration
- TMDB streaming provider search
- CLI интерфейс через Click
- Кэширование профилей и LLM response
- Verbose debugging mode
- Session-based Instagram authentication

---

# 🏗 Архитектура

```text
CLI (Click)
    ↓
instagram_parser.py
    ↓
Claude API (Anthropic)
    ↓
streaming_search.py (TMDB API)
    ↓
Console output
````

---

# 📦 Структура проекта

```text
GirlsFilm/
├── main.py
├── instagram_parser.py
├── streaming_search.py
├── cache_utils.py
├── create_session.py
├── cache/
│   ├── profiles/
│   └── llm/
├── .env.example
├── .gitignore
├── README.md
└── pyproject.toml
```

---

# ⚙️ Установка

## 1. Клонирование

```bash
git clone <repo>
cd GirlsFilm
```

## 2. Установка зависимостей

```bash
uv sync
```

или:

```bash
pip install -r requirements.txt
```

---

# 🔑 Настройка .env

Создай `.env`:

```env
ANTHROPIC_API_KEY=your_claude_key
TMDB_API_KEY_2=your_tmdb_key
```

---

# 🎬 TMDB API

Получить API key:

[https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

Используется:

* search/multi
* watch/providers

---

# 🔐 Instagram Session

Instaloader использует persistent session.

## Вариант 1 (рекомендуется)

```bash
instaloader --load-cookies chrome
```

или:

```bash
instaloader --load-cookies firefox
```

---

# ▶️ Использование

## Базовый запуск

```bash
python main.py antonina_zolotova_
```

## Verbose mode

```bash
python main.py antonina_zolotova_ -v
```

## Без кэша

```bash
python main.py antonina_zolotova_ --no-cache
```

---

# 🧠 Что анализирует AI

Claude получает:

* bio
* hashtags
* captions
* followers count
* post count

И определяет:

* интересы
* настроение
* lifestyle
* подходящий сериал/фильм

---

# 📡 Streaming Search

TMDB API используется для:

* поиска сериала/фильма
* определения platform providers
* проверки availability по регионам

Поддерживаемые платформы:

* Netflix
* HBO Max
* Amazon Prime Video

---

# 💾 Кэширование

## Instagram profiles

TTL:

* 24 часа

## Claude responses

TTL:

* 7 дней

Инвалидация:

* profile hash
* prompt hash

---

# 📋 Пример вывода

```text
💘 Date Night Assistant
========================================

📱 Сканирую профиль @antonina_zolotova_...

✅ Профиль загружен.
🤖 Claude проанализировал профиль

🎬 РЕКОМЕНДАЦИЯ НА ВЕЧЕР

📺 Сериал: Вращение
(Spinning Out)

🎭 Жанр: спортивная драма

📡 Где смотреть:
✅ Netflix — https://www.netflix.com

🎞️ TMDB:
https://www.themoviedb.org/tv/83050
```

---

# 🛠 Используемые технологии

* Python 3.12
* Click
* Instaloader
* Anthropic Claude API
* TMDB API
* requests
* python-dotenv

---

# ⚠️ Ограничения

* Работает только с публичными Instagram профилями
* Instagram может rate-limit scraping
* Streaming availability зависит от региона
* Claude может рекомендовать малоизвестные фильмы без provider data

---

# 📌 Примечание

Проект создавался как AI-oriented engineering test task с упором на:

* external integrations
* prompt engineering
* orchestration
* caching
* CLI UX
* structured AI output
