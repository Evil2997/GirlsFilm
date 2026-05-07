import argparse
import sys

from app.config import settings
from app.logger import logger, setup_logger
from app.instagram import get_profile_data
from app.claude_client import analyze_profile
from app.streaming import find_on_streaming
from app.cache import load_profile_cache, save_profile_cache
from app.database import init_db, save_recommendation, get_history


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="date-night",
        description="Find the perfect series for a date night based on Instagram profile.",
    )
    parser.add_argument("--username", help="Instagram username (without @)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--history", action="store_true", help="Show recommendation history")
    return parser.parse_args()


def run() -> None:
    args = _parse_args()

    if args.verbose:
        setup_logger(verbose=True)

    use_cache = not args.no_cache
    username = args.username.lstrip("@")

    init_db()

    if args.history:
        rows = get_history(username)
        if not rows:
            logger.info(f"No history for @{username}")
            return
        logger.info(f"\n📋 History for @{username}:")
        for row in rows:
            logger.info(f"  [{row['created_at'][:10]}] {row['series_ru']} ({row['series']}) — {row['providers']}")
        return

    logger.info(f"\n💘 Date Night Assistant")
    logger.info("=" * 40)
    logger.info(f"📱 Scanning profile @{username}...")

    profile_data = None

    if use_cache:
        profile_data = load_profile_cache(username)
        if profile_data:
            logger.info("📦 Profile loaded from cache")

    if not profile_data:
        profile_data = get_profile_data(username)
        if not profile_data:
            logger.error("❌ Could not retrieve profile data.")
            sys.exit(1)
        if use_cache:
            save_profile_cache(username, profile_data)

    if args.verbose:
        logger.debug(f"\n📊 Profile data:")
        logger.debug(f"  Name: {profile_data.get('full_name')}")
        logger.debug(f"  Bio: {profile_data.get('biography')}")
        logger.debug(f"  Hashtags: {', '.join(profile_data.get('hashtags', [])[:10])}")

    logger.info("✅ Profile loaded. Analysing interests...")

    recommendation = analyze_profile(username, profile_data, use_cache=use_cache)
    logger.info("🤖 Claude analysed the profile")

    series_title = recommendation["series_title"]
    logger.info(f"🔍 Searching '{series_title}' on Netflix and HBO...")

    streaming_info = find_on_streaming(series_title, verbose=args.verbose)

    providers = [p["name"] for p in streaming_info.get("providers", [])]
    save_recommendation(username, recommendation, providers)

    logger.info(f"\n{'=' * 40}")
    logger.info("🎬 TONIGHT'S RECOMMENDATION")
    logger.info("=" * 40)
    logger.info(f"\n📺 Series: {recommendation['series_title_ru']}")
    logger.info(f"   ({recommendation['series_title']})")
    logger.info(f"\n🎭 Genre: {recommendation['genre']}")
    logger.info(f"\n💡 Interests of @{username}:")
    for interest in recommendation["interests"]:
        logger.info(f"   • {interest}")
    logger.info(f"\n❤️  Why it fits:")
    logger.info(f"   {recommendation['reason']}")
    logger.info(f"\n📡 Where to watch:")

    if streaming_info["found"]:
        for provider in streaming_info["providers"]:
            logger.info(f"   ✅ {provider['name']} — {provider['url']}")
    else:
        logger.info("   ⚠️  Not found on Netflix / HBO / Prime")

    if streaming_info.get("tmdb_url"):
        logger.info(f"\n🎞️  TMDB: {streaming_info['tmdb_url']}")

    logger.info(f"\n{'=' * 40}")
    logger.info("🌙 Enjoy your evening! 🍷\n")
