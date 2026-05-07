import os
import subprocess
from pathlib import Path

import instaloader
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER = os.getenv("INSTAGRAM_USER")
INSTAGRAM_PASS = os.getenv("INSTAGRAM_PASS")

SESSION_DIR = Path.home() / ".config" / "instaloader"


def session_file(username: str) -> Path:
    return SESSION_DIR / f"session-{username}"


def session_exists(username: str) -> bool:
    return session_file(username).exists()


def validate_session(username: str) -> bool:
    try:
        loader = instaloader.Instaloader()

        loader.load_session_from_file(username)

        profile = instaloader.Profile.from_username(
            loader.context,
            username
        )

        print(f"✅ Session валидна для @{profile.username}")

        return True

    except Exception as e:

        print(f"❌ Session невалидна: {e}")

        return False


def try_browser_import(browser: str) -> bool:
    try:
        print(f"\n🌐 Пробую импорт cookies из {browser}...")
        result = subprocess.run(
            [
                "instaloader",
                f"--load-cookies={browser}",
            ],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print(f"✅ Cookies импортированы из {browser}")
            return True
        print(f"❌ Не удалось импортировать cookies из {browser}")
        return False
    except Exception as e:
        print(f"❌ Ошибка {browser}: {e}")
        return False


def terminal_login(username: str):
    try:
        print(f"\n🔐 Терминальный логин для @{username}")
        loader = instaloader.Instaloader()

        try:
            loader.load_session_from_file(username)
            print("📦 Найдена существующая session")
            profile = instaloader.Profile.from_username(loader.context, username)
            print(f"✅ Уже залогинен как @{profile.username}")
            return True
        except Exception:
            pass

        if not INSTAGRAM_PASS:
            print("❌ INSTAGRAM_PASS отсутствует в .env")
            return False

        loader.login(username, INSTAGRAM_PASS)
        loader.save_session_to_file()
        print("✅ Session успешно создана")
        return True

    except Exception as e:
        print(f"❌ Ошибка терминального логина: {e}")
        return False


def main():
    print("\n💘 Instagram Session Manager")
    print("=" * 40)
    username = INSTAGRAM_USER
    if username:
        username = username.strip().replace("@", "")
    else:
        print("❌ INSTAGRAM_USER отсутствует в .env")
        return

    print(f"\n🔎 Проверяю session для @{username}")
    if session_exists(username):
        print("📦 Session file найден")
        if validate_session(username):
            return

        print("⚠️ Session существует, но невалидна")
    else:
        print("📭 Session file не найден")
    print("\n🌐 Пытаюсь получить session через браузер")

    imported = (
            try_browser_import("chrome")
            or try_browser_import("firefox")
    )

    if imported:

        print("\n🔎 Проверяю появилась ли session")

        if session_exists(username):

            if validate_session(username):
                return

        print("⚠️ Session импортирована, но username не совпадает")

    print("\n⚠️ Browser import не помог")

    answer = input(
        "\nПопробовать терминальный логин? [Y/n]: "
    ).strip().lower()

    if answer in {"", "y", "yes"}:

        terminal_login(username)

    else:

        print("❌ Session не создана")


if __name__ == "__main__":
    main()
