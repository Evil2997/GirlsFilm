import json
import anthropic

from app.config import settings, CLAUDE_MODEL, CLAUDE_MAX_TOKENS
from app.prompts import build_recommendation_prompt
from app.cache import (
    load_llm_cache,
    save_llm_cache,
    get_profile_hash,
    get_prompt_hash,
)
from app.logger import logger

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def analyze_profile(username: str, profile_data: dict, use_cache: bool = True) -> dict:
    prompt = build_recommendation_prompt(profile_data)
    profile_hash = get_profile_hash(profile_data)
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
    result = json.loads(response_text[start:end])

    if use_cache:
        save_llm_cache(username, profile_hash, prompt_hash, result)

    return result
