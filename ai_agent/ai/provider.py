"""Модуль взаимодействия с AI-провайдерами через OpenRouter."""

import os
import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentAction(BaseModel):
    """Схема действия, которое должен выполнить агент."""

    thought: str
    action_type: str
    element_id: Optional[int] = None
    text: Optional[str] = None
    url: Optional[str] = None


class LLMProvider:
    """Класс для управления запросами к языковой модели."""

    def __init__(self):
        """Инициализирует клиента OpenAI для работы с OpenRouter."""
        api_key = os.getenv("AI_API_KEY")
        base_url = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1")

        if not api_key:
            raise ValueError("AI_API_KEY не установлен")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Web AI Agent",
            }
        )
        self.model = os.getenv("AI_MODEL_NAME", "google/gemini-2.0-flash-001")

    async def get_next_action(
        self, system_prompt: str, user_context: str
    ) -> AgentAction:
        """Запрашивает следующее действие у модели."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            content = response.choices[0].message.content
            logger.info("Ответ получен: %s", content[:100])

            data = json.loads(content)
            return AgentAction(**data)

        except Exception as exc:
            logger.error("Ошибка OpenRouter: %s", exc)
            raise
