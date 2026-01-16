# (c) 2026 Sviatoslav Orel. All rights reserved.
# This code is proprietary and not for commercial use.

import asyncio
import os
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Отключаем лишние логи от httpx для чистоты вывода
logging.getLogger("httpx").setLevel(logging.WARNING)


async def test():
    # Загружаем переменные из .env
    load_dotenv()
    
    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model_name = os.getenv("AI_MODEL_NAME", "google/gemini-2.0-flash-exp:free")

    print(f"--- Тестирование конфигурации ---")
    print(f"URL: {base_url}")
    print(f"Model: {model_name}")
    print(f"Key starts with: {api_key[:8]}...") 
    print(f"---------------------------------\n")

    # Инициализируем клиент с заголовками для OpenRouter
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Browser AI Agent Test",
        }
    )

    try:
        resp = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Напиши слово 'Готово', если ты меня слышишь."}],
            max_tokens=10,
            temperature=0.1
        )
        print("✅ Успех!")
        print("Ответ модели:", resp.choices[0].message.content)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test())
