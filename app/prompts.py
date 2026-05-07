from app.models import InstagramProfile


def build_recommendation_prompt(profile: InstagramProfile) -> str:
    hashtags = ", ".join(profile.hashtags[:20])
    captions = " | ".join(profile.captions[:5])

    return f"""You are an assistant that selects the perfect series or film for a date night.

Instagram profile data:
- Name: {profile.full_name or "Unknown"}
- Bio: {profile.biography or "No bio"}
- Post count: {profile.post_count}
- Followers: {profile.followers}
- Hashtags from posts: {hashtags}
- Post captions: {captions}

Based on this data:
1. Identify the person's interests
2. Recommend ONE ideal series or film for a date night
3. Explain why this choice fits

Respond strictly in JSON format:
{{
    "interests": ["interest1", "interest2", "interest3"],
    "series_title": "Title in English",
    "series_title_ru": "Title in Russian",
    "reason": "Why this fits (2-3 sentences)",
    "genre": "genre"
}}"""