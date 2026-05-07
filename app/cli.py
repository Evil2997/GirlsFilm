import argparse
import sys

from app.cache import load_profile_cache, save_profile_cache
from app.claude_client import analyze_profile
from app.database import init_db, save_recommendation, get_history
from app.instagram import get_profile_data
from app.logger import logger, setup_logger
from app.session import build_loader
from app.streaming import find_on_streaming


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="date-night",
        description="Find the perfect series for a date night based on Instagram profile.",
    )
    parser.add_argument("--username", required=True, help="Instagram username (without @)")
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
        records = get_history(username)
        if not records:
            logger.info(f"No history for @{username}")
            return
        logger.info(f"\n📋 History for @{username}:")
        for r in records:
            logger.info(
                f"  [{r.created_at}]  {r.series_ru} ({r.series})"
                + (f"  —  {r.providers}" if r.providers else "")
            )
        return

    logger.info("\n💘 Date Night Assistant")
    logger.info("=" * 40)

    # ── Profile ────────────────────────────────────────────────
    profile = load_profile_cache(username) if use_cache else None

    if profile:
        logger.info(f"📦 Profile @{username} loaded from cache")
    else:
        logger.info(f"📱 Establishing Instagram session...")
        loader = build_loader()
        if not loader:
            logger.error("❌ Could not establish Instagram session")
            sys.exit(1)

        logger.info(f"🔍 Scanning profile @{username}...")
        profile = get_profile_data(loader, username)
        if not profile:
            logger.error("❌ Could not retrieve profile data")
            sys.exit(1)

        if use_cache:
            save_profile_cache(username, profile)

    if args.verbose:
        logger.debug(f"  Name     : {profile.full_name}")
        logger.debug(f"  Bio      : {profile.biography}")
        logger.debug(f"  Hashtags : {', '.join(profile.hashtags[:10])}")

    # ── Claude ─────────────────────────────────────────────────
    logger.info("🤖 Analysing interests with Claude...")
    recommendation = analyze_profile(username, profile, use_cache=use_cache)

    # ── Streaming ──────────────────────────────────────────────
    logger.info(f"🔍 Searching '{recommendation.series_title}' on Netflix and HBO...")
    streaming = find_on_streaming(recommendation.series_title, verbose=args.verbose)

    providers = [p.name for p in streaming.providers]
    save_recommendation(username, recommendation, providers)

    # ── Output ─────────────────────────────────────────────────
    logger.info(f"\n{'=' * 40}")
    logger.info("🎬 TONIGHT'S RECOMMENDATION")
    logger.info("=" * 40)
    logger.info(f"\n📺 Series : {recommendation.series_title_ru}")
    logger.info(f"           ({recommendation.series_title})")
    logger.info(f"\n🎭 Genre  : {recommendation.genre}")
    logger.info(f"\n💡 Interests of @{username}:")
    for interest in recommendation.interests:
        logger.info(f"   • {interest}")
    logger.info("\n❤️  Why it fits:")
    logger.info(f"   {recommendation.reason}")
    logger.info("\n📡 Where to watch:")
    if streaming.found:
        for p in streaming.providers:
            logger.info(f"   ✅ {p.name} — {p.url}")
    else:
        logger.info("   ⚠️  Not found on Netflix / HBO / Prime")
    if streaming.tmdb_url:
        logger.info(f"\n🎞️  TMDB: {streaming.tmdb_url}")
    logger.info(f"\n{'=' * 40}")
    logger.info("🌙 Enjoy your evening! 🍷\n")
