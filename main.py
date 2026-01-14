"""Точка входа в приложение.

Инициализирует компоненты и запускает интерактивный сеанс с агентом.
"""

import asyncio
import logging

from dotenv import load_dotenv

from ai_agent.ai.provider import LLMProvider
from ai_agent.browser.manager import BrowserManager
from ai_agent.core.agent import WebAgent

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


async def main():
    """Основная функция запуска."""
    load_dotenv()

    print("\n" + "=" * 50)
    print("🤖 AI BROWSER AGENT СИСТЕМА ЗАПУЩЕНА")
    print("=" * 50)

    print("\nВведите вашу задачу для агента:")
    loop = asyncio.get_event_loop()
    task = await loop.run_in_executor(None, input, "> ")

    if not task:
        print("❌ Ошибка: Задача не может быть пустой.")
        return

    print(f"\n🚀 Начинаю выполнение: {task}\n")

    browser = BrowserManager(headless=False)
    llm = LLMProvider()
    agent = WebAgent(browser, llm)

    try:
        # Определение стартового URL
        is_mail = "почт" in task.lower()
        start_url = "https://mail.yandex.ru" if is_mail else "https://ya.ru"

        await browser.start(start_url)

        result = await agent.run(task)
        print(f"\n✅ ФИНАЛЬНЫЙ РЕЗУЛЬТАТ: {result}")

    except KeyboardInterrupt:
        print("\n🛑 Работа прервана пользователем.")
    except Exception as e:
        logging.error("Ошибка в основном цикле: %s", e)
        print(f"\n❌ Произошла ошибка при выполнении: {e}")
    finally:
        await browser.close()
        print("👋 Сессия завершена.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
