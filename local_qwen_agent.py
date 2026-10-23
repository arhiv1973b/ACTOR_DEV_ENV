import ollama
import json
import hashlib
import os

def get_file_hash(filepath: str) -> str:
    if not os.path.exists(filepath):
        return json.dumps({"error": f"Файл не найден: {filepath}"})
    with open(filepath, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return json.dumps({"filepath": filepath, "sha256": file_hash})

available_tools = {
    "get_file_hash": get_file_hash
}

def run_agent(prompt: str):
    print(f"\n🤖 ЗАДАЧА АГЕНТА: {prompt}")
    
    tools_schema = [{
        "type": "function",
        "function": {
            "name": "get_file_hash",
            "description": "Вычисляет SHA-256 хэш файла для криминалистической проверки целостности.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Путь к файлу"
                    }
                },
                "required": ["filepath"]
            }
        }
    }]
    
    try:
        response = ollama.chat(
            model='qwen2.5:3b',
            messages=[{'role': 'user', 'content': prompt}],
            tools=tools_schema
        )
        
        message = response['message']
        
        if not message.get('tool_calls'):
            print(f"\nОтвет модели (без инструментов): {message['content']}")
            return
            
        print("\n🛠️  ВЫЗОВ ИНСТРУМЕНТОВ:")
        for tool in message['tool_calls']:
            func_name = tool['function']['name']
            args = tool['function']['arguments']
            print(f" -> {func_name}({args})")
            
            if func_name in available_tools:
                result = available_tools[func_name](**args)
                print(f" <- Результат: {result}")
                
                final_response = ollama.chat(
                    model='qwen2.5:3b',
                    messages=[
                        {'role': 'user', 'content': prompt},
                        message,
                        {'role': 'tool', 'content': result, 'name': func_name}
                    ]
                )
                print(f"\n✅ ИТОГОВЫЙ ОТВЕТ: {final_response['message']['content']}\n")
    except Exception as e:
        print(f"Ошибка выполнения: {str(e)}")

if __name__ == '__main__':
    run_agent("Вычисли SHA-256 хэш для файла requirements.txt")
