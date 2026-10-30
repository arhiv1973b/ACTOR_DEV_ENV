import os
import json
from pathlib import Path


def safe_delete_duplicates():
    env_dir = Path(r"H:\ACTOR_DEV_ENV")
    map_path = env_dir / "duplication_map.json"
    pointers_dir = env_dir / "pointers"

    if not map_path.exists():
        print(f"❌ Карта дубликатов не найдена: {map_path}")
        return

    print("🚀 Запуск безопасного удаления физических дубликатов...")
    container = json.loads(map_path.read_text(encoding="utf-8"))

    deleted_count = 0
    freed_bytes = 0

    for group in container.get("duplication_map", []):
        master = group["master_file"]

        for dup in group["duplicates"]:
            dup_path = Path(dup)
            pointer_path = pointers_dir / f"{dup_path.name}.pointer.json"

            # Защита 1: Проверка на совпадение с мастер-файлом
            if str(dup_path.resolve()) == str(Path(master).resolve()):
                print(
                    f"⚠️ КРИТИЧЕСКАЯ ЗАЩИТА: Блокировка попытки удаления мастер-файла: {dup}"
                )
                continue

            # Защита 2: Наличие резервного указателя
            if not pointer_path.exists():
                print(f"⚠️ Пропуск {dup_path.name}: Локальный файл-указатель не найден!")
                continue

            if dup_path.exists():
                try:
                    file_size = dup_path.stat().st_size
                    dup_path.unlink()  # Безвозвратное физическое удаление
                    deleted_count += 1
                    freed_bytes += file_size
                    print(
                        f"  🗑️ Удален: {dup_path.name} (Освобождено: {round(file_size / 1024 / 1024, 2)} МБ)"
                    )
                except Exception as e:
                    print(f"  [!] Ошибка удаления {dup_path.name}: {e}")
            else:
                print(f"  ℹ️ Уже отсутствует: {dup_path.name}")

        # Обновляем статус группы
        group["status"] = "PHYSICALLY_DELETED"

    # Сохраняем обновленный реестр
    map_path.write_text(
        json.dumps(container, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    print("=" * 70)
    print(f"✅ Цикл завершен. Удалено избыточных файлов: {deleted_count}")
    print(f"💾 Фактически освобождено на диске F:: {freed_mb} МБ")
    print("🔄 Статус в duplication_map.json обновлен.")


if __name__ == "__main__":
    safe_delete_duplicates()
