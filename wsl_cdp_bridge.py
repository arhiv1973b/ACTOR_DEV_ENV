import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "http://127.0.0.1:9223"
    print(f"[СИСТЕМА]: Подключаюсь к {url}...")
    
    async with async_playwright() as p:
        # Даем Chrome 2 секунды на "разогрев" после запуска
        await asyncio.sleep(2)
        
        try:
            # Пытаемся подключиться один раз с таймаутом
            browser = await p.chromium.connect_over_cdp(url)
            print("[СИСТЕМА]: УСПЕХ! Подключение установлено.")
            
            # Держим связь
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"[ОШИБКА]: {e}")
            print("Совет: Если ошибка повторится, проверьте, что Chrome запущен с --remote-debugging-port=9223")

if __name__ == "__main__":
    asyncio.run(main())
