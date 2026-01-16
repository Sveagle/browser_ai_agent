# (c) 2026 Sviatoslav Orel. All rights reserved.
# This code is proprietary and not for commercial use.

"""Модуль управления жизненным циклом браузера.

Содержит класс BrowserManager, который инкапсулирует работу с Playwright,
обеспечивая открытие страниц и управление сессией.
"""

import logging
from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    async_playwright,
)

logger = logging.getLogger(__name__)


class BrowserManager:
    """Класс для инициализации и управления состоянием браузера."""

    def __init__(self, headless: bool = False):
        """Инициализирует менеджер браузера.

        Args:
            headless (bool): Запуск браузера в фоновом режиме.
                По умолчанию False.
        """
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self, url: str = "https://ya.ru") -> Page:
        """Запускает браузер и создает новую страницу.

        Returns:
            Page: Объект страницы Playwright.
        """
        logger.info("Запуск браузера Chromium...")
        self._playwright = await async_playwright().start()

        self.context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir="./user_data",
            headless=self.headless,
            viewport={'width': 1280, 'height': 720}
        )

        self.page = self.context.pages[0]

        # Ключевая правка: сразу идем на нужный сайт
        logger.info("Переход на %s", url)
        await self.page.goto(url)

        return self.page

    async def close(self) -> None:
        """Закрывает контекст и останавливает Playwright."""
        if self.context:
            await self.context.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Браузер и сессия успешно закрыты.")
