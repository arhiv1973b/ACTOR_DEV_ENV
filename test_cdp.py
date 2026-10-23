import asyncio
import websockets

async def test():
    # Стучимся через socat (localhost)
    uri = "ws://127.0.0.1:9222/devtools/browser"
    print(f"Попытка подключения к {uri}...")
    try:
        async with websockets.connect(uri) as ws:
            print("Успех! Соединение установлено.")
    except Exception as e:
        print(f"Ошибка соединения: {e}")

asyncio.run(test())
