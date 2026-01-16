# (c) 2026 Sviatoslav Orel. All rights reserved.
# This code is proprietary and not for commercial use.

"""Модуль для парсинга и фильтрации DOM-дерева."""

from typing import Dict, List
from playwright.async_api import Page


class DomParser:
    """Класс для извлечения информации о доступных элементах на странице."""

    @staticmethod
    async def get_interactive_elements(page: Page) -> List[Dict]:
        js_script = """
        () => {
            // Сужаем селекторы, чтобы не хватать всё подряд
            const selectors = 'button, a, input, [role="button"], [role="checkbox"], .mail-MessageSnippet-Item';
            const elements = Array.from(document.querySelectorAll(selectors));
            const seenTexts = new Set();

            return elements.map((el, index) => {
                const rect = el.getBoundingClientRect();
                let text = (el.innerText || el.placeholder || el.value || el.getAttribute('aria-label') || "").trim();

                // Обработка писем Яндекса
                if (el.classList.contains('mail-MessageSnippet-Item')) {
                    const content = el.innerText.replace(/\\n/g, ' ').trim();
                    text = `ПИСЬМО: ${content}`;
                }

                // Короткий текст для экономии токенов
                text = text.replace(/\\s\\s+/g, ' ').substring(0, 60);

                return {
                    id: index,
                    tagName: el.tagName,
                    text: text,
                    role: el.getAttribute('role') || el.type || 'none',
                    // Проверка видимости: элемент должен быть в зоне видимости
                    isVisible: rect.width > 2 && rect.height > 2 &&
                               rect.top >= 0 && rect.bottom <= window.innerHeight,
                    x: rect.left + rect.width / 2,
                    y: rect.top + rect.height / 2
                };
            }).filter(el => {
                // ЖЕСТКАЯ ФИЛЬТРАЦИЯ
                if (!el.isVisible || el.text.length < 3) return false;

                // Игнорируем бесполезные для задачи элементы
                const junk = ['помощь', 'обратная связь', 'правообладателям', 'вакансии', 'реклама'];
                if (junk.some(word => el.text.toLowerCase().includes(word))) return false;

                if (seenTexts.has(el.text)) return false;
                seenTexts.add(el.text);
                return true;
            }).slice(0, 60); // БЕРЕМ ТОЛЬКО ПЕРВЫЕ 60 ЭЛЕМЕНТОВ
        }
        """
        return await page.evaluate(js_script)

    @staticmethod
    def format_elements_for_llm(elements: List[Dict]) -> str:
        """Форматирует элементы максимально компактно."""
        if not elements:
            return "На странице нет доступных элементов."

        lines = [f"Доступно элементов: {len(elements)}"]
        for el in elements:
            # Ужимаем формат до минимума
            clean_text = el["text"].replace("'", "").replace('"', "")
            lines.append(f"ID:{el['id']}|{el['role']}|'{clean_text}'")

        return "\n".join(lines)
