import asyncio
from playwright.async_api import async_playwright


async def main():
    url = "https://share.gemini.google/wHbd1BotyzWh"
    try:
        async with async_playwright() as p:
            # Запуск Chromium в фоновом режиме
            browser = await p.chromium.launch(headless=True)

            # Корректное создание контекста и страницы в Python
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            print(f"Загрузка URL: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Явное ожидание завершения работы JS-скриптов страницы
            await page.wait_for_timeout(5000)

            # Извлечение отрендеренного текста
            text = await page.locator("body").inner_text()

            print("\n--- ИЗВЛЕЧЕННЫЙ ТЕКСТ ---")
            print(text)
            print("--- КОНЕЦ ---")

            await browser.close()
    except Exception as e:
        print(f"Ошибка выполнения: {e}")


if __name__ == "__main__":
    asyncio.run(main())
