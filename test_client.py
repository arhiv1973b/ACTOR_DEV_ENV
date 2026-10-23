import socket
import json


def send_command(command):
    try:
        # Подключаемся к оркестратору на локальный порт 5000
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 5000))
        client.send(json.dumps(command).encode('utf-8'))
        response = client.recv(4096).decode('utf-8')
        client.close()
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Проверка связи
print("Тестирование связи с оркестратором...")
result = send_command({"action": "ping"})
print(f"Ответ сервера: {result}")
