import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Final

MAIN_DIR: Final[Path] = Path(__file__).resolve().parents[0]

CACHE_DIR = MAIN_DIR / "cache"
PROFILE_CACHE_DIR = CACHE_DIR / "profiles"
LLM_CACHE_DIR = CACHE_DIR / "llm"

PROFILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROFILE_CACHE_TTL = 3600 * 24  # 1 day
LLM_CACHE_TTL = 3600 * 24 * 7  # 7 days


def _load_json(path: Path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _is_expired(timestamp, ttl: int):
    if isinstance(timestamp, int | float):
        age = time.time() - timestamp
        return age > ttl

    cached_time = datetime.fromisoformat(timestamp)
    age = (datetime.now() - cached_time).total_seconds()
    return age > ttl

def get_profile_hash(profile_data: dict) -> str:
    payload = json.dumps(profile_data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(payload.encode()).hexdigest()


def get_prompt_hash(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()


def load_profile_cache(username: str):
    path = PROFILE_CACHE_DIR / f"{username}.json"

    data = _load_json(path)

    if not data:
        return None

    if _is_expired(data["cached_at"], PROFILE_CACHE_TTL):
        path.unlink(missing_ok=True)
        return None

    return data["profile_data"]


def save_profile_cache(username: str, profile_data: dict):
    path = PROFILE_CACHE_DIR / f"{username}.json"

    _save_json(path, {
        "cached_at": time.time(),
        "profile_data": profile_data
    })


def load_llm_cache(username: str, profile_hash: str, prompt_hash: str):
    path = LLM_CACHE_DIR / f"{username}.json"

    data = _load_json(path)

    if not data:
        return None

    if _is_expired(data["cached_at"], LLM_CACHE_TTL):
        path.unlink(missing_ok=True)
        return None

    if data["profile_hash"] != profile_hash:
        return None

    if data["prompt_hash"] != prompt_hash:
        return None

    return data["response"]


def save_llm_cache(
    username: str,
    profile_hash: str,
    prompt_hash: str,
    response: dict
):
    path = LLM_CACHE_DIR / f"{username}.json"

    _save_json(path, {
        "cached_at": time.time(),
        "profile_hash": profile_hash,
        "prompt_hash": prompt_hash,
        "response": response
    })