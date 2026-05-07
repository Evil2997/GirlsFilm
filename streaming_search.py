import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY_2")

PROVIDER_MAP = {
    "Netflix": "https://www.netflix.com",
    "HBO Max": "https://play.max.com",
    "Amazon Prime Video": "https://www.primevideo.com",
}

PRIORITY_ORDER = ["Netflix", "HBO Max", "Amazon Prime Video"]


def find_on_streaming(title: str, verbose: bool = False) -> dict:
    result = {
        "found": False,
        "providers": [],
        "tmdb_url": None,
        "matched_title": None,
        "media_type": None,
    }

    if not TMDB_API_KEY:
        if verbose:
            print("❌ TMDB_API_KEY_2 не найден в .env")
        return result

    try:
        if verbose:
            print(f"\n🔎 Ищу в TMDB: {title}")

        search_response = requests.get(
            "https://api.themoviedb.org/3/search/multi",
            params={
                "api_key": TMDB_API_KEY,
                "query": title,
                "language": "en-US",
            },
            timeout=10,
        )

        if verbose:
            print(f"📡 Search status: {search_response.status_code}")

        if search_response.status_code != 200:
            if verbose:
                print(search_response.text[:500])
            return result

        results = search_response.json().get("results", [])

        if verbose:
            print(f"🔍 Найдено результатов: {len(results)}")

        selected = next(
            (item for item in results if item.get("media_type") in {"tv", "movie"}),
            None,
        )

        if not selected:
            return result

        media_id = selected["id"]
        media_type = selected["media_type"]
        matched_title = selected.get("name") or selected.get("title")

        result["matched_title"] = matched_title
        result["media_type"] = media_type
        result["tmdb_url"] = f"https://www.themoviedb.org/{media_type}/{media_id}"

        if verbose:
            print(f"🎯 Выбран: {matched_title}")
            print(f"🆔 ID: {media_id}")
            print(f"📺 Type: {media_type}")

        providers_response = requests.get(
            f"https://api.themoviedb.org/3/{media_type}/{media_id}/watch/providers",
            params={"api_key": TMDB_API_KEY},
            timeout=10,
        )

        if verbose:
            print(f"📡 Providers status: {providers_response.status_code}")

        if providers_response.status_code != 200:
            if verbose:
                print(providers_response.text[:500])
            return result

        regions = providers_response.json().get("results", {})

        region_code = "DE" if "DE" in regions else "US" if "US" in regions else None

        if verbose:
            print(f"🌍 Выбран регион: {region_code}")

        if not region_code:
            return result

        flatrate = regions[region_code].get("flatrate", [])

        if verbose:
            print("💰 Провайдеры:")
            for provider in flatrate:
                print(f"   • {provider.get('provider_name')}")

        found = {
            provider.get("provider_name")
            for provider in flatrate
            if provider.get("provider_name") in PROVIDER_MAP
        }

        for provider_name in PRIORITY_ORDER:
            if provider_name in found:
                result["providers"].append({
                    "name": provider_name,
                    "url": PROVIDER_MAP[provider_name],
                })

        result["found"] = bool(result["providers"])
        return result

    except requests.RequestException as e:
        if verbose:
            print(f"❌ Request error: {e}")
        return result


if __name__ == "__main__":
    for title in ["Spinning Out", "Stranger Things", "The Last of Us", "The Boys"]:
        print(find_on_streaming(title, verbose=True))
        print("-" * 60)