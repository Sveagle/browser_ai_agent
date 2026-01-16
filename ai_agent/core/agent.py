# (c) 2026 Sviatoslav Orel. All rights reserved.
# This code is proprietary and not for commercial use.

"""Модуль основного оркестратора ИИ-агента.

Реализует автономный цикл принятия решений с памятью действий.
"""

import asyncio
import logging
from typing import List, Optional

from ai_agent.ai.prompts import SYSTEM_PROMPT
from ai_agent.ai.provider import AgentAction, LLMProvider
from ai_agent.browser.actions import BrowserActions
from ai_agent.browser.manager import BrowserManager
from ai_agent.utils.dom_parser import DomParser
from ai_agent.utils.logger import log_thought

logger = logging.getLogger(__name__)


class WebAgent:
    """Класс автономного агента с функциями контроля безопасности и памяти."""

    def __init__(
        self,
        browser_manager: BrowserManager,
        llm_provider: LLMProvider,
        max_steps: int = 15
    ):
        """Инициализирует агента."""
        self.browser = browser_manager
        self.llm = llm_provider
        self.max_steps = max_steps
        # История действий для предотвращения зацикливания
        self.history: List[str] = []
        # Список стоп-слов
        self.danger_keywords = ["delete", "pay", "купить", "корзина", "удалить"]

    async def run(self, task: str) -> str:
        """Запускает цикл выполнения задачи."""
        page = self.browser.page
        if not page:
            raise RuntimeError("Браузер не запущен. Вызовите browser.start()")

        current_step = 0
        last_error: Optional[str] = None

        while current_step < self.max_steps:
            current_step += 1
            logger.info("--- Шаг %d из %d ---", current_step, self.max_steps)

            # Получаем состояние страницы
            elements = await DomParser.get_interactive_elements(page)
            page_state = DomParser.format_elements_for_llm(elements)

            # Формируем расширенный контекст с историей
            last_actions = self.history[-5:]
            history_str = (
                "\n".join(last_actions) if last_actions
                else "Действий еще не было."
            )

            context = (
                f"Задача: {task}\n\n"
                f"ПОСЛЕДНИЕ ДЕЙСТВИЯ:\n{history_str}\n\n"
                f"ТЕКУЩИЙ URL: {page.url}\n\n"
                f"{page_state}"
            )

            if last_error:
                context += f"\n\nОШИБКА НА ПРОШЛОМ ШАГЕ: {last_error}"

            try:
                action: AgentAction = await self.llm.get_next_action(
                    SYSTEM_PROMPT, context
                )
                log_thought(action.thought)
            except (RuntimeError, ValueError) as exc:
                logger.error("Ошибка логики LLM: %s", exc)
                break

            if action.action_type == "finish":
                return f"Задача завершена: {action.thought}"

            # --- SECURITY LAYER ---
            if self._is_destructive_action(action):
                print(f"\n⚠️ SECURITY! Опасное действие: {action.thought}")
                loop = asyncio.get_event_loop()
                confirm = await loop.run_in_executor(
                    None, input, "Разрешить выполнение? (y/n): "
                )
                if confirm.lower() != 'y':
                    last_error = "Действие отклонено пользователем."
                    continue

            # Исполнение и запись в историю
            target_text = self._get_element_text(action.element_id, elements)
            hist_msg = (
                f"Шаг {current_step}: {action.action_type} "
                f"по '{target_text}' (ID: {action.element_id})"
            )
            self.history.append(hist_msg)

            last_error = await self._execute_action(action, elements)

            # Ждем стабилизации страницы после клика
            await BrowserActions.wait_for_load(page)
            await asyncio.sleep(1)

        return "Достигнут лимит шагов."

    def _get_element_text(self, el_id: Optional[int], elements: List[dict]):
        """Вспомогательный метод для получения текста элемента по ID."""
        if el_id is None:
            return "N/A"
        target = next((e for e in elements if e["id"] == el_id), None)
        return target["text"] if target else "Неизвестный элемент"

    def _is_destructive_action(self, action: AgentAction) -> bool:
        """Проверяет деструктивные действия."""
        thought_lower = action.thought.lower()
        is_danger = any(word in thought_lower for word in self.danger_keywords)
        return is_danger and action.action_type == "click"

    async def _execute_action(
        self,
        action: AgentAction,
        elements: List[dict]
    ) -> Optional[str]:
        """Исполняет действие в браузере."""
        page = self.browser.page
        try:
            if action.action_type == "navigate" and action.url:
                await page.goto(action.url)
                return None

            target = next(
                (e for e in elements if e["id"] == action.element_id),
                None
            )

            if not target and action.action_type in ["click", "type"]:
                return f"Элемент с ID {action.element_id} исчез"

            if action.action_type == "click" and target:
                logger.info("Клик: %s (ID: %s)", target['text'], target['id'])
                await BrowserActions.click_at(page, target["x"], target["y"])

            elif action.action_type == "type" and action.text and target:
                logger.info("Ввод в ID %s", action.element_id)
                await BrowserActions.type_text(
                    page, target["x"], target["y"], action.text
                )

            elif action.action_type == "wait":
                await asyncio.sleep(3)

            return None
        except Exception as exc:
            return f"Ошибка Playwright: {str(exc)}"
