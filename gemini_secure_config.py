#!/usr/bin/env python3
"""
Gemini CLI Safe Config Manager
Соответствует Secret Protection & Dynamic Retrieval Protocol
"""

import os
import sys
import json
from pathlib import Path

class GeminiSecureConfig:
    """Безопасная конфигурация Gemini с защитой ключей."""
    
    def __init__(self):
        self.protocol_name = "Secret Protection & Dynamic Retrieval Protocol"
        self.audit_results = {}
        self.config_path = Path(os.path.expanduser("~/.gemini/config.json"))
    
    def stage_1_audit(self):
        """ЭТАП 1: Тотальный аудит существующих ключей."""
        print("\n" + "=" * 70)
        print("🔍 ЭТАП 1: ПРЕДВАРИТЕЛЬНЫЙ АУДИТ (Pre-Execution Audit)")
        print("=" * 70)
        
        keys_to_check = [
            "GEMINI_API_KEY",
            "GEMINI_ACCESS_TOKEN",
            "Gemini_API_Key_2",
            "GOOGLE_GENERATIVE_AI_API_KEY",
        ]
        
        found_keys = {}
        for key in keys_to_check:
            value = os.getenv(key)
            if value:
                found_keys[key] = {
                    "status": "FOUND",
                    "length": len(value),
                    "prefix": value[:15] + "..."
                }
                self.audit_results[key] = value
        
        if found_keys:
            print(f"✅ Найдено {len(found_keys)} валидных ключей в системе:")
            for key, info in found_keys.items():
                print(f"   [{info['status']}] {key}: {info['length']} символов ({info['prefix']})")
            return True
        else:
            print("❌ Ключи не найдены. Переход к ЭТАПУ 2.")
            return False
    
    def stage_2_local_search(self):
        """ЭТАП 2: Локальный поиск в конфигурационных файлах."""
        print("\n" + "=" * 70)
        print("🔎 ЭТАП 2: ЛОКАЛЬНЫЙ ПОИСК (Assigned Automated Search)")
        print("=" * 70)
        
        search_paths = [
            self.config_path,
            Path.home() / ".gemini" / "credentials.json",
            Path.home() / ".config" / "gemini" / "api_key",
            Path(".env"),
        ]
        
        for path in search_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if "GEMINI" in content or "API_KEY" in content:
                            print(f"   ✅ Конфиг найден: {path}")
                            if path.suffix == ".json":
                                data = json.load(f)
                                for k, v in data.items():
                                    if isinstance(v, str) and len(v) > 30:
                                        self.audit_results[k] = v
                except Exception as e:
                    print(f"   ⚠️  Ошибка чтения {path}: {e}")
        
        return len(self.audit_results) > 0
    
    def stage_3_dynamic_insertion(self):
        """ЭТАП 3: Динамическая подстановка ключа."""
        print("\n" + "=" * 70)
        print("📌 ЭТАП 3: ДИНАМИЧЕСКАЯ ПОДСТАНОВКА (Dynamic Insertion)")
        print("=" * 70)
        
        # Используем первый найденный ключ
        primary_key = self.audit_results.get("GEMINI_API_KEY")
        
        if not primary_key:
            primary_key = next(iter(self.audit_results.values()), None)
        
        if primary_key:
            print(f"✅ Выбран ключ для динамической подстановки:")
            print(f"   Префикс: {primary_key[:20]}...")
            print(f"   Источник: {os.getenv('GEMINI_API_KEY') and 'Environment Variable' or 'File-based config'}")
            
            # Создать безопасный контекст
            os.environ["GEMINI_ACTIVE_KEY"] = primary_key
            print("✅ Ключ загружен в контекст выполнения (в памяти, не на диске)")
            return True
        
        return False
    
    def stage_4_emergency_break(self):
        """ЭТАП 4: Безопасная остановка, если ключ не найден."""
        print("\n" + "=" * 70)
        print("🛑 ЭТАП 4: БЕЗОПАСНАЯ ОСТАНОВКА (Emergency Break & Hard Stop)")
        print("=" * 70)
        
        if not self.audit_results:
            print("❌ КРИТИЧЕСКИЙ ОСТАНОВ: Требуемый валидный ключ не найден в системе.")
            print("   Перезапись конфигурации заблокирована во избежание повреждения данных.")
            print("   Ожидание действий оператора.")
            sys.exit(1)
        else:
            print("✅ Ключи найдены. Безопасная остановка не требуется.")
    
    def run_full_protocol(self):
        """Запустить полный протокол."""
        print("\n" + "╔" + "=" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + f" {self.protocol_name}".ljust(69) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "=" * 68 + "╝")
        
        # Выполнить этапы по порядку
        stage_1_ok = self.stage_1_audit()
        
        if not stage_1_ok:
            stage_2_ok = self.stage_2_local_search()
            if not stage_2_ok:
                self.stage_4_emergency_break()
        
        stage_3_ok = self.stage_3_dynamic_insertion()
        
        if not stage_3_ok:
            self.stage_4_emergency_break()
        
        print("\n" + "=" * 70)
        print("✅ ПРОТОКОЛ ЗАВЕРШЕН УСПЕШНО")
        print("=" * 70)
        
        return self.audit_results

if __name__ == "__main__":
    manager = GeminiSecureConfig()
    results = manager.run_full_protocol()
    
    print("\n📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(json.dumps(
        {k: v[:20] + "..." if len(v) > 20 else v 
         for k, v in results.items()},
        indent=2
    ))
