"""
Date Night Assistant
Сканирует Instagram профиль, рекомендует сериал через Claude API,
находит его на Netflix/HBO.
"""

import json

import anthropic
import click
from dotenv import load_dotenv

from cache_utils import (
    load_profile_cache,
    save_profile_cache,
    load_llm_cache,
    save_llm_cache,
    get_profile_hash,
    get_prompt_hash,
)
from instagram_parser import get_profile_data
from streaming_search import find_on_streaming

load_dotenv()
client = anthropic.Anthropic()  # берёт ANTHROPIC_API_KEY из env


def analyze_profile_with_claude(username: str, profile_data: dict, use_cache: bool = True) -> dict:
    """Отправляем данные профиля в Claude, получаем рекомендацию."""

    prompt = f"""Ты помощник для выбора сериала на вечер свидания.

Вот данные Instagram профиля девушки:
- Имя: {profile_data.get('full_name', 'Неизвестно')}
- Bio: {profile_data.get('biography', 'Нет описания')}
- Количество постов: {profile_data.get('post_count', 0)}
- Подписчики: {profile_data.get('followers', 0)}
- Хэштеги из постов: {', '.join(profile_data.get('hashtags', [])[:20])}
- Описания постов: {' | '.join(profile_data.get('captions', [])[:5])}

На основе этих данных:
1. Определи интересы девушки
2. Порекомендуй ОДИН идеальный сериал или фильм для совместного просмотра
3. Объясни почему именно этот сериал или фильм подходит

Ответь строго в формате JSON:
{{
    "interests": ["интерес1", "интерес2", "интерес3"],
    "series_title": "Название сериала на английском",
    "series_title_ru": "Название на русском",
    "reason": "Почему этот сериал подходит (2-3 предложения)",
    "genre": "жанр"
}}"""

    profile_hash = get_profile_hash(profile_data)
    prompt_hash = get_prompt_hash(prompt)

    if use_cache:
        cached_response = load_llm_cache(
            username=username,
            profile_hash=profile_hash,
            prompt_hash=prompt_hash
        )

        if cached_response:
            print("📦 Claude response загружен из кэша")
            return cached_response

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    json_str = response_text[start:end]

    parsed_response = json.loads(json_str)

    if use_cache:
        save_llm_cache(
            username=username,
            profile_hash=profile_hash,
            prompt_hash=prompt_hash,
            response=parsed_response
        )

    return parsed_response


@click.command()
@click.argument('username')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
@click.option('--cache/--no-cache', default=True, help='Использовать кэш')
def main(username: str, verbose: bool, cache: bool):
    """
    Date Night Assistant — найди идеальный сериал для свидания.

    USERNAME — Instagram username девушки (без @)

    Пример: python main.py natasha_example
    """

    click.echo(f"\n💘 Date Night Assistant")
    click.echo(f"{'=' * 40}")
    click.echo(f"📱 Сканирую профиль @{username}...")

    # Шаг 1: Парсим Instagram
    profile_data = None

    if cache:
        profile_data = load_profile_cache(username)

        if profile_data:
            click.echo("📦 Профиль загружен из кэша")

    if not profile_data:
        profile_data = get_profile_data(username)

        if not profile_data:
            click.echo("❌ Не удалось получить данные профиля.")
            return

        if cache:
            save_profile_cache(username, profile_data)

    if verbose:
        click.echo(f"\n📊 Данные профиля:")
        click.echo(f"  Имя: {profile_data.get('full_name')}")
        click.echo(f"  Bio: {profile_data.get('biography')}")
        click.echo(f"  Хэштеги: {', '.join(profile_data.get('hashtags', [])[:10])}")

    click.echo(f"✅ Профиль загружен. Анализирую интересы...")

    # Шаг 2: Анализируем через Claude
    recommendation = analyze_profile_with_claude(
        username=username,
        profile_data=profile_data,
        use_cache=cache
    )

    click.echo(f"🤖 Claude проанализировал профиль")

    # Шаг 3: Ищем на стриминговых сервисах
    series_title = recommendation['series_title']
    click.echo(f"🔍 Ищу '{series_title}' на Netflix и HBO...")

    streaming_info = find_on_streaming(series_title, verbose=verbose)

    # Шаг 4: Выводим результат
    click.echo(f"\n{'=' * 40}")
    click.echo(f"🎬 РЕКОМЕНДАЦИЯ НА ВЕЧЕР")
    click.echo(f"{'=' * 40}")
    click.echo(f"\n📺 Сериал: {recommendation['series_title_ru']}")
    click.echo(f"   ({recommendation['series_title']})")
    click.echo(f"\n🎭 Жанр: {recommendation['genre']}")
    click.echo(f"\n💡 Интересы @{username}:")
    for interest in recommendation['interests']:
        click.echo(f"   • {interest}")
    click.echo(f"\n❤️  Почему подходит:")
    click.echo(f"   {recommendation['reason']}")

    click.echo(f"\n📡 Где смотреть:")

    if streaming_info["found"]:

        for provider in streaming_info["providers"]:
            click.echo(
                f"   ✅ {provider['name']} — {provider['url']}"
            )

    else:
        click.echo("   ⚠️ Не найдено на Netflix/HBO/Prime")

    if streaming_info.get("tmdb_url"):
        click.echo(
            f"\n🎞️ TMDB: {streaming_info['tmdb_url']}"
        )
    click.echo(f"\n{'=' * 40}")
    click.echo(f"🌙 Хорошего вечера! 🍷\n")


if __name__ == '__main__':
    main()
