import subprocess
from pathlib import Path

import instaloader

from app.config import settings, FATAL_STATUS_CODES, _SESSION_DIR
from app.logger import logger


def _session_file() -> Path:
    return _SESSION_DIR / f"session-{settings.instagram_user}"


def _delete_session() -> None:
    path = _session_file()
    if path.exists():
        path.unlink()
        logger.debug("Stale session file deleted")


def _is_logged_in(loader: instaloader.Instaloader) -> bool:
    """
    Check session state without any network request.
    Profile.from_username() makes an API call and contributes to rate limiting — avoid it here.
    """
    try:
        if loader.context.is_logged_in:
            username = getattr(loader.context, "username", settings.instagram_user)
            logger.info(f"Session valid — logged in as @{username}")
            return True
        logger.warning("Session loaded but is_logged_in = False")
        return False
    except Exception as e:
        logger.warning(f"Could not check session state: {e}")
        return False


def _load_from_file(loader: instaloader.Instaloader) -> bool:
    if not _session_file().exists():
        logger.debug(f"No session file for @{settings.instagram_user}")
        return False
    try:
        loader.load_session_from_file(settings.instagram_user)
        if _is_logged_in(loader):
            return True
        _delete_session()
        return False
    except Exception as e:
        logger.warning(f"Could not load session file: {e}")
        _delete_session()
        return False


def _try_browser(loader: instaloader.Instaloader, browser: str) -> bool:
    """
    Import session from browser cookies.
    Trusts is_logged_in — does NOT call Profile.from_username().
    """
    try:
        result = subprocess.run(
            ["instaloader", f"--load-cookies={browser}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.debug(f"{browser}: subprocess failed (rc={result.returncode})")
            return False
        if not _session_file().exists():
            logger.debug(f"{browser}: no session file created")
            return False
        loader.load_session_from_file(settings.instagram_user)
        logger.info(f"Session imported from {browser}")
        if _is_logged_in(loader):
            return True
        _delete_session()
        return False
    except Exception as e:
        logger.debug(f"{browser} error: {e}")
        return False


def build_loader() -> instaloader.Instaloader | None:
    """
    Build an authenticated Instaloader instance.
    Order: session file → Chrome → Firefox.
    """
    if not settings.instagram_user:
        logger.error("INSTAGRAM_USER not set in .env")
        return None

    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
        fatal_status_codes=FATAL_STATUS_CODES,
    )

    if _load_from_file(loader):
        return loader

    for browser in ("chrome", "firefox"):
        if _try_browser(loader, browser):
            return loader

    logger.error(
        "❌ Could not establish Instagram session.\n"
        "   Make sure you are logged in to Instagram in Chrome, then run:\n"
        "   instaloader --load-cookies chrome"
    )
    return None
