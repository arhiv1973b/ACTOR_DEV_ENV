import asyncio
import sys
from playwright.async_api import async_playwright

async def main():
    try:
        async with async_playwright() as p:
            print("[СИСТЕМА]: Инициализация подключения к 127.0.0.1:9222...")
            # Принудительное использование IPv4 (127.0.0.1) для стабильности
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=30000)
            print("[СИСТЕМА]: Мост активен. Идентичность A©tor подключена.")
            
            # Держим соединение открытым
            while True:
                await asyncio.sleep(1)
    except Exception as e:
        print(f"[ОШИБКА]: Мост упал: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
