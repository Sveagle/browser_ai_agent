"""Модуль настройки логирования.

Обеспечивает форматированный вывод работы агента в консоль.
"""

import logging


def setup_agent_logger() -> None:
    """Настраивает базовый конфиг логирования для проекта."""
    logger = logging.getLogger("ai_agent")
    logger.setLevel(logging.INFO)

    # Формат: Время [УРОВЕНЬ] Сообщение
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)


def log_thought(thought: str) -> None:
    """Специальный вывод для 'размышлений' модели.

    Args:
        thought (str): Текст рассуждения агента.
    """
    print(f"\n🤔 МЫСЛЬ АГЕНТА: {thought}\n" + "-" * 40)
