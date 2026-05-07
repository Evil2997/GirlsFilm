def build_recommendation_prompt(profile_data: dict) -> str:
    hashtags = ", ".join(profile_data.get("hashtags", [])[:20])
    captions = " | ".join(profile_data.get("captions", [])[:5])

    return f"""You are an assistant that selects the perfect series or film for a date night.

Instagram profile data:
- Name: {profile_data.get("full_name", "Unknown")}
- Bio: {profile_data.get("biography", "No bio")}
- Post count: {profile_data.get("post_count", 0)}
- Followers: {profile_data.get("followers", 0)}
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
