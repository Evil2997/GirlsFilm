import json
import anthropic

from app.config import settings, CLAUDE_MODEL, CLAUDE_MAX_TOKENS
from app.prompts import build_recommendation_prompt
from app.models import InstagramProfile, Recommendation
from app.cache import (
    load_llm_cache,
    save_llm_cache,
    get_profile_hash,
    get_prompt_hash,
)
from app.logger import logger

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def analyze_profile(
    username: str,
    profile: InstagramProfile,
    use_cache: bool = True,
) -> Recommendation:
    prompt = build_recommendation_prompt(profile)
    profile_hash = get_profile_hash(profile)
    prompt_hash = get_prompt_hash(prompt)

    if use_cache:
        cached = load_llm_cache(username, profile_hash, prompt_hash)
        if cached:
            logger.info("📦 Claude response loaded from cache")
            return cached

    message = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    data = json.loads(response_text[start:end])
    recommendation = Recommendation.model_validate(data)

    if use_cache:
        save_llm_cache(username, profile_hash, prompt_hash, recommendation)

    return recommendation