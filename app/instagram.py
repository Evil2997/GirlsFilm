import instaloader
from typing import Optional

from app.config import settings, INSTAGRAM_POSTS_LIMIT, FATAL_STATUS_CODES
from app.logger import logger


def get_profile_data(username: str) -> Optional[dict]:
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

    try:
        loader.load_session_from_file(settings.instagram_user)
    except Exception as e:
        logger.warning(f"Session not loaded: {e}")

    try:
        profile = instaloader.Profile.from_username(loader.context, username)

        if profile.is_private:
            logger.warning(f"Profile @{username} is private")
            return None

        data: dict = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "followers": profile.followers,
            "following": profile.followees,
            "post_count": profile.mediacount,
            "hashtags": [],
            "captions": [],
        }

        for i, post in enumerate(profile.get_posts()):
            if i >= INSTAGRAM_POSTS_LIMIT:
                break
            if post.caption_hashtags:
                data["hashtags"].extend(post.caption_hashtags)
            if post.caption:
                data["captions"].append(post.caption[:100])

        data["hashtags"] = list(set(data["hashtags"]))
        return data

    except instaloader.exceptions.ProfileNotExistsException:
        logger.error(f"Profile @{username} not found")
        return None
    except instaloader.exceptions.ConnectionException as e:
        logger.error(f"Connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
