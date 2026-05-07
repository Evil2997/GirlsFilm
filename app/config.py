from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR: Path = Path(__file__).resolve().parents[1]
CACHE_DIR: Path = ROOT_DIR / "cache"
PROFILE_CACHE_DIR: Path = CACHE_DIR / "profiles"
LLM_CACHE_DIR: Path = CACHE_DIR / "llm"
DB_PATH: Path = ROOT_DIR / "history.db"

PROFILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROFILE_CACHE_TTL: int = 3600 * 24        # 1 day
LLM_CACHE_TTL: int = 3600 * 24 * 7        # 7 days
INSTAGRAM_POSTS_LIMIT: int = 12
CLAUDE_MODEL: str = "claude-opus-4-5"
CLAUDE_MAX_TOKENS: int = 1024

PROVIDER_MAP: dict[str, str] = {
    "Netflix": "https://www.netflix.com",
    "HBO Max": "https://play.max.com",
    "Amazon Prime Video": "https://www.primevideo.com",
}
PROVIDER_PRIORITY: list[str] = ["Netflix", "HBO Max", "Amazon Prime Video"]
TMDB_SEARCH_URL: str = "https://api.themoviedb.org/3/search/multi"
TMDB_PROVIDERS_URL: str = "https://api.themoviedb.org/3/{media_type}/{media_id}/watch/providers"
TMDB_ITEM_URL: str = "https://www.themoviedb.org/{media_type}/{media_id}"
PREFERRED_REGIONS: list[str] = ["DE", "US", "GB"]

FATAL_STATUS_CODES = [400, 401, 403, 404, 429]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str
    tmdb_api_key_2: str
    instagram_user: str = ""
    instagram_pass: str = ""


settings = Settings()
