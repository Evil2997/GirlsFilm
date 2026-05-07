import json
import time
import hashlib
from pathlib import Path

from app.config import (
    PROFILE_CACHE_DIR,
    LLM_CACHE_DIR,
    PROFILE_CACHE_TTL,
    LLM_CACHE_TTL,
)


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _is_expired(timestamp: float, ttl: int) -> bool:
    return (time.time() - float(timestamp)) > ttl


def get_profile_hash(profile_data: dict) -> str:
    payload = json.dumps(profile_data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(payload.encode()).hexdigest()


def get_prompt_hash(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()


def load_profile_cache(username: str) -> dict | None:
    path = PROFILE_CACHE_DIR / f"{username}.json"
    data = _load_json(path)
    if not data:
        return None
    if _is_expired(data["cached_at"], PROFILE_CACHE_TTL):
        path.unlink(missing_ok=True)
        return None
    return data["profile_data"]


def save_profile_cache(username: str, profile_data: dict) -> None:
    path = PROFILE_CACHE_DIR / f"{username}.json"
    _save_json(path, {"cached_at": time.time(), "profile_data": profile_data})


def load_llm_cache(username: str, profile_hash: str, prompt_hash: str) -> dict | None:
    path = LLM_CACHE_DIR / f"{username}.json"
    data = _load_json(path)
    if not data:
        return None
    if _is_expired(data["cached_at"], LLM_CACHE_TTL):
        path.unlink(missing_ok=True)
        return None
    if data["profile_hash"] != profile_hash or data["prompt_hash"] != prompt_hash:
        return None
    return data["response"]


def save_llm_cache(
    username: str,
    profile_hash: str,
    prompt_hash: str,
    response: dict,
) -> None:
    path = LLM_CACHE_DIR / f"{username}.json"
    _save_json(path, {
        "cached_at": time.time(),
        "profile_hash": profile_hash,
        "prompt_hash": prompt_hash,
        "response": response,
    })
