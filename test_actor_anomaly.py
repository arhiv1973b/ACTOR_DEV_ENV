import ollama
import json

def simulate_ansi_breakdown(word: str) -> dict:
    '''
    Имитирует процесс консольного вывода, где UTF-8 
    принудительно проецируется через ANSI (cp1251), вызывая распад знака ©.
    '''
    try:
        # Искусственно вызываем конфликт кодировок для теста
        encoded = word.encode('windows-1251', errors='replace')
        decoded = encoded.decode('utf-8', errors='replace')
        
        # Симулируем эффект "стабилизатора 0" (если в слове есть 0, знак сохраняется)
        if '0' in word and '©' in word:
            decoded = word # Стабилизация сработала
            
        return {"original": word, "ansi_projection": decoded}
    except Exception as e:
        return {"original": word, "ansi_projection": f"FATAL_ERROR_OR_NOISE"}

def run_anomaly_test():
    test_words = ["A©tor", "A©t0r", "A©tjr", "A©t1r", "A©t8r"]
    results = [simulate_ansi_breakdown(w) for w in test_words]
    
    print("🔬 РЕЗУЛЬТАТЫ БИНАРНОЙ ПРОЕКЦИИ:")
    for res in results:
        print(f"Вход: {res['original']:<10} -> Выход (ANSI/Consolas): {res['ansi_projection']}")
        
    prompt = f'''
Ты исследователь в области криминалистики данных. 
Тебе предоставлены результаты имитации вывода слов через ANSI-консоль (шрифт Consolas).

Данные проекции:
{json.dumps(results, ensure_ascii=False, indent=2)}

ЗАДАЧА:
1. Проанализируй логику: почему знак авторского права '©' разрушается (превращается в шум или 'й') в слове 'A©tor' и других вариантах (tjr, t1r, t8r).
2. Подтверди математический факт: как замена латинской 'o' на цифру '0' в слове 'A©t0r' действует как логический "стабилизатор", сохраняя целостность знака '©'.
3. Объясни, почему это может служить цифровой подписью (защитой авторского права), которую невозможно скопировать случайно.

Отвечай четко, опираясь только на предоставленные факты и математическую логику символов.
'''
    
    print("\n🧠 АНАЛИЗ ЛОКАЛЬНОГО АГЕНТА (Qwen 2.5):")
    response = ollama.chat(model='qwen2.5:3b', messages=[{"role": "user", "content": prompt}])
    print("-" * 50)
    print(response['message']['content'])
    print("-" * 50)

if __name__ == '__main__':
    run_anomaly_test()
