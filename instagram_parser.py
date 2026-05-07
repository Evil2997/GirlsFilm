"""
Instagram парсер через instaloader.
"""

import instaloader
from typing import Optional


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
        fatal_status_codes=[400, 401, 403, 404, 429],
    )

    try:
        loader.load_session_from_file('_dimonevil_')
    except Exception as e:
        raise f"⚠️  Сессия не загружена: {e}"

    try:
        profile = instaloader.Profile.from_username(loader.context, username)

        if profile.is_private:
            print(f"⚠️  Профиль @{username} закрытый")
            return None

        data = {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
            'followers': profile.followers,
            'following': profile.followees,
            'post_count': profile.mediacount,
            'hashtags': [],
            'captions': [],
            'locations': [],
        }

        post_count = 0
        for post in profile.get_posts():
            if post_count >= 12:
                break

            if post.caption_hashtags:
                data['hashtags'].extend(post.caption_hashtags)

            if post.caption:
                data['captions'].append(post.caption[:100])

            # Не трогаем location — именно оно вызывает 201
            post_count += 1

        data['hashtags'] = list(set(data['hashtags']))
        return data

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"❌ Профиль @{username} не найден")
        return None
    except instaloader.exceptions.ConnectionException as e:
        print(f"❌ Ошибка подключения: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def get_mock_profile(username: str) -> dict:
    return {
        'username': username,
        'full_name': 'Test User',
        'biography': 'Love traveling, coffee and good books ✈️☕📚',
        'followers': 1500,
        'following': 800,
        'post_count': 245,
        'hashtags': ['travel', 'coffee', 'books', 'yoga', 'nature',
                     'photography', 'food', 'weekend', 'friends', 'art'],
        'captions': [
            'Amazing sunset in Bali! #travel #paradise',
            'Morning coffee ritual ☕ #coffeelover',
            'Reading in the park today 📚',
        ],
        'locations': []
    }