import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import (
    PROFILE_CACHE_DIR,
    LLM_CACHE_DIR,
    PROFILE_CACHE_TTL,
    LLM_CACHE_TTL,
)
from app.models import InstagramProfile, Recommendation, ProfileCache, LlmCache


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_expired(cached_at: datetime, ttl: int) -> bool:
    age = (_now() - cached_at.replace(tzinfo=timezone.utc)).total_seconds()
    return age > ttl


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def get_profile_hash(profile: InstagramProfile) -> str:
    payload = profile.model_dump_json(exclude_none=True)
    return hashlib.md5(payload.encode()).hexdigest()


def get_prompt_hash(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()


def load_profile_cache(username: str) -> InstagramProfile | None:
    path = PROFILE_CACHE_DIR / f"{username}.json"
    raw = _load_json(path)
    if not raw:
        return None
    entry = ProfileCache.model_validate(raw)
    if _is_expired(entry.cached_at, PROFILE_CACHE_TTL):
        path.unlink(missing_ok=True)
        return None
    return entry.profile_data


def save_profile_cache(username: str, profile: InstagramProfile) -> None:
    path = PROFILE_CACHE_DIR / f"{username}.json"
    entry = ProfileCache(cached_at=_now(), profile_data=profile)
    _save_json(path, entry.model_dump_json(indent=2))


def load_llm_cache(
        username: str,
        profile_hash: str,
        prompt_hash: str,
) -> Recommendation | None:
    path = LLM_CACHE_DIR / f"{username}.json"
    raw = _load_json(path)
    if not raw:
        return None
    entry = LlmCache.model_validate(raw)
    if _is_expired(entry.cached_at, LLM_CACHE_TTL):
        path.unlink(missing_ok=True)
        return None
    if entry.profile_hash != profile_hash or entry.prompt_hash != prompt_hash:
        return None
    return entry.response


def save_llm_cache(
        username: str,
        profile_hash: str,
        prompt_hash: str,
        response: Recommendation,
) -> None:
    path = LLM_CACHE_DIR / f"{username}.json"
    entry = LlmCache(
        cached_at=_now(),
        profile_hash=profile_hash,
        prompt_hash=prompt_hash,
        response=response,
    )
    _save_json(path, entry.model_dump_json(indent=2))
