from datetime import datetime
from pydantic import BaseModel, Field


class InstagramProfile(BaseModel):
    """Public Instagram profile data collected for analysis."""

    username: str = Field(description="Instagram username without @")
    full_name: str = Field(description="Display name from profile")
    biography: str = Field(default="", description="Profile bio text")
    followers: int = Field(default=0, description="Follower count")
    following: int = Field(default=0, description="Following count")
    post_count: int = Field(default=0, description="Total number of posts")
    hashtags: list[str] = Field(
        default_factory=list,
        description="Unique hashtags collected from recent posts",
    )
    captions: list[str] = Field(
        default_factory=list,
        description="First 100 chars of captions from recent posts",
    )


class Recommendation(BaseModel):
    """Series or film recommendation produced by Claude."""

    interests: list[str] = Field(
        description="Inferred interests of the person based on their profile"
    )
    series_title: str = Field(description="Title of the recommended series or film in English")
    series_title_ru: str = Field(description="Title in Russian")
    reason: str = Field(description="Why this recommendation fits the person (2-3 sentences)")
    genre: str = Field(description="Genre of the recommended content")


class StreamingProvider(BaseModel):
    """A single streaming platform where the content is available."""

    name: str = Field(description="Provider display name, e.g. Netflix")
    url: str = Field(description="Homepage URL of the streaming service")


class StreamingResult(BaseModel):
    """Result of a TMDB streaming availability lookup."""

    found: bool = Field(
        default=False,
        description="True if the content was found on at least one supported provider",
    )
    providers: list[StreamingProvider] = Field(
        default_factory=list,
        description="Supported providers where the content is available",
    )
    tmdb_url: str | None = Field(
        default=None,
        description="TMDB page URL for the matched content",
    )
    matched_title: str | None = Field(
        default=None,
        description="Title as returned by TMDB (may differ slightly from query)",
    )
    media_type: str | None = Field(
        default=None,
        description="TMDB media type: 'tv' or 'movie'",
    )


class ProfileCache(BaseModel):
    """Wrapper stored in the profile cache file."""

    cached_at: datetime = Field(description="UTC timestamp when the cache entry was written")
    profile_data: InstagramProfile = Field(description="Cached Instagram profile")


class LlmCache(BaseModel):
    """Wrapper stored in the LLM response cache file."""

    cached_at: datetime = Field(description="UTC timestamp when the cache entry was written")
    profile_hash: str = Field(description="MD5 of the serialised profile used to detect staleness")
    prompt_hash: str = Field(description="MD5 of the prompt text used to detect prompt changes")
    response: Recommendation = Field(description="Cached Claude recommendation")


class HistoryRecord(BaseModel):
    """A single row from the recommendations history table."""

    id: int = Field(description="Auto-incremented primary key")
    username: str = Field(description="Instagram username the recommendation was made for")
    series: str = Field(description="Recommended series title in English")
    series_ru: str = Field(description="Recommended series title in Russian")
    genre: str = Field(default="", description="Genre of the recommendation")
    reason: str = Field(default="", description="Why this recommendation was chosen")
    providers: str = Field(default="", description="Comma-separated list of available providers")
    created_at: datetime = Field(description="UTC timestamp when the recommendation was saved")