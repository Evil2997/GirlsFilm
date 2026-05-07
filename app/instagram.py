from typing import Optional

import instaloader

from app.config import INSTAGRAM_POSTS_LIMIT
from app.logger import logger
from app.models import InstagramProfile


def _fetch_user_node(
    loader: instaloader.Instaloader,
    username: str,
) -> dict | None:
    """
    Call i.instagram.com/api/v1/users/web_profile_info/ directly,
    bypassing Profile.from_username() which is broken in Instaloader 4.15.1.
    Returns the raw 'user' dict or None.
    """
    try:
        data = loader.context.get_iphone_json(
            path=f"api/v1/users/web_profile_info/?username={username}",
            params={},
        )
        # Response structure: {"data": {"user": {...}}} or {"user": {...}}
        user = (
            data.get("data", {}).get("user")
            or data.get("user")
        )
        return user
    except Exception as e:
        logger.debug(f"Direct iPhone API call failed: {e}")
        return None


def get_profile_data(
    loader: instaloader.Instaloader,
    username: str,
) -> Optional[InstagramProfile]:
    try:
        # Primary path: use Instaloader's high-level API
        profile = instaloader.Profile.from_username(loader.context, username)

    except instaloader.exceptions.ProfileNotExistsException:
        # Instaloader 4.15.1 bug: GraphQL endpoint returns 403 → raises
        # ProfileNotExistsException even for existing profiles.
        # Fall back to a direct iPhone API call.
        logger.debug(
            f"Profile.from_username() failed for @{username} "
            f"(likely Instaloader 4.15.1 GraphQL bug) — trying fallback..."
        )
        user_node = _fetch_user_node(loader, username)
        if not user_node:
            logger.error(
                f"Profile @{username} not found via fallback either. "
                f"If the profile exists, try: instaloader --load-cookies chrome"
            )
            return None
        return _parse_user_node(loader, username, user_node)

    except instaloader.exceptions.ConnectionException as e:
        logger.error(f"Connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

    if profile.is_private:
        logger.warning(f"Profile @{username} is private")
        return None

    hashtags: list[str] = []
    captions: list[str] = []

    try:
        for i, post in enumerate(profile.get_posts()):
            if i >= INSTAGRAM_POSTS_LIMIT:
                break
            if post.caption_hashtags:
                hashtags.extend(post.caption_hashtags)
            if post.caption:
                captions.append(post.caption[:100])
    except Exception as e:
        logger.warning(f"Could not fetch posts for @{username}: {e}")
        # Posts are optional — return profile without them

    return InstagramProfile(
        username=profile.username,
        full_name=profile.full_name or "",
        biography=profile.biography or "",
        followers=profile.followers,
        following=profile.followees,
        post_count=profile.mediacount,
        hashtags=list(set(hashtags)),
        captions=captions,
    )


def _parse_user_node(
    loader: instaloader.Instaloader,
    username: str,
    user: dict,
) -> Optional[InstagramProfile]:
    """Build InstagramProfile from a raw API user dict (fallback path)."""
    if not user:
        return None

    is_private = user.get("is_private", False)
    if is_private:
        logger.warning(f"Profile @{username} is private")
        return None

    hashtags: list[str] = []
    captions: list[str] = []

    # Try to fetch posts via Profile.from_id (different endpoint, often still works)
    user_id = user.get("pk") or user.get("id")
    if user_id:
        try:
            profile = instaloader.Profile.from_id(loader.context, int(user_id))
            for i, post in enumerate(profile.get_posts()):
                if i >= INSTAGRAM_POSTS_LIMIT:
                    break
                if post.caption_hashtags:
                    hashtags.extend(post.caption_hashtags)
                if post.caption:
                    captions.append(post.caption[:100])
        except Exception as e:
            logger.warning(f"Could not fetch posts via from_id for @{username}: {e}")

    return InstagramProfile(
        username=user.get("username", username),
        full_name=user.get("full_name") or "",
        biography=user.get("biography") or "",
        followers=user.get("follower_count") or user.get("edge_followed_by", {}).get("count", 0),
        following=user.get("following_count") or user.get("edge_follow", {}).get("count", 0),
        post_count=user.get("media_count") or user.get("edge_owner_to_timeline_media", {}).get("count", 0),
        hashtags=list(set(hashtags)),
        captions=captions,
    )