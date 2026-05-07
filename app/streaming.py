import requests

from app.config import (
    settings,
    PROVIDER_MAP,
    PROVIDER_PRIORITY,
    TMDB_SEARCH_URL,
    TMDB_PROVIDERS_URL,
    TMDB_ITEM_URL,
    PREFERRED_REGIONS,
)
from app.logger import logger
from app.models import StreamingProvider, StreamingResult


def find_on_streaming(title: str, verbose: bool = False) -> StreamingResult:
    result = StreamingResult()

    try:
        search_resp = requests.get(
            TMDB_SEARCH_URL,
            params={
                "api_key": settings.tmdb_api_key_2,
                "query": title,
                "language": "en-US",
            },
            timeout=10,
        )

        if search_resp.status_code != 200:
            logger.debug(f"TMDB search failed: {search_resp.status_code}")
            return result

        items = search_resp.json().get("results", [])
        selected = next(
            (i for i in items if i.get("media_type") in {"tv", "movie"}), None
        )

        if not selected:
            return result

        media_id = selected["id"]
        media_type = selected["media_type"]
        matched_title = selected.get("name") or selected.get("title")

        result.matched_title = matched_title
        result.media_type = media_type
        result.tmdb_url = TMDB_ITEM_URL.format(
            media_type=media_type, media_id=media_id
        )

        if verbose:
            logger.debug(f"TMDB match: {matched_title} ({media_type} id={media_id})")

        providers_resp = requests.get(
            TMDB_PROVIDERS_URL.format(media_type=media_type, media_id=media_id),
            params={"api_key": settings.tmdb_api_key_2},
            timeout=10,
        )

        if providers_resp.status_code != 200:
            return result

        regions = providers_resp.json().get("results", {})
        region = next((r for r in PREFERRED_REGIONS if r in regions), None)

        if not region:
            return result

        flatrate = regions[region].get("flatrate", [])
        available = {
            p["provider_name"]
            for p in flatrate
            if p["provider_name"] in PROVIDER_MAP
        }

        if verbose:
            logger.debug(f"Available providers in {region}: {available}")

        for name in PROVIDER_PRIORITY:
            if name in available:
                result.providers.append(
                    StreamingProvider(name=name, url=PROVIDER_MAP[name])
                )

        result.found = bool(result.providers)
        return result

    except requests.RequestException as e:
        logger.debug(f"Request error: {e}")
        return result
