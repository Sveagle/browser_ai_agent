"""Модуль атомарных действий браузера.

Содержит вспомогательный класс для выполнения низкоуровневых
манипуляций с элементами страницы.
"""

import asyncio
import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class BrowserActions:
    """Класс для выполнения физических действий на странице."""

    @staticmethod
    async def click_at(page: Page, x: float, y: float) -> None:
        """Выполняет клик по координатам.

        Args:
            page (Page): Страница Playwright.
            x (float): Координата X.
            y (float): Координата Y.
        """
        await page.mouse.click(x, y)
        logger.info("Клик по координатам: [%s, %s]", x, y)

    @staticmethod
    async def type_text(page: Page, x: float, y: float, text: str) -> None:
        """Кликает в поле и вводит текст.

        Args:
            page (Page): Страница Playwright.
            x (float): Координата X.
            y (float): Координата Y.
            text (str): Текст для ввода.
        """
        await page.mouse.click(x, y)
        # Очистка поля перед вводом (Ctrl+A -> Backspace)
        await page.keyboard.down("Control")
        await page.keyboard.press("a")
        await page.keyboard.up("Control")
        await page.keyboard.press("Backspace")

        await page.keyboard.type(text, delay=50)
        logger.info("Ввод текста в координаты [%s, %s]", x, y)

    @staticmethod
    async def wait_for_load(page: Page, timeout: int = 3000) -> None:
        """Ожидает стабилизации страницы.

        Args:
            page (Page): Страница Playwright.
            timeout (int): Время ожидания в мс.
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception:
            # Игнорируем таймауты сетевого ожидания
            await asyncio.sleep(1)
