from mcp.server.fastmcp import FastMCP
import os

# Инициализация сервера
mcp = FastMCP("TI-ULA-Bridge")

# Инструмент для чтения файлов
@mcp.tool()
def read_file(path: str) -> str:
    """Читает содержимое файла из директории проекта."""
    full_path = os.path.join("H:\\ACTOR_DEV_ENV", path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

# Инструмент для записи/обновления кода
@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Записывает код или данные в файл проекта."""
    full_path = os.path.join("H:\\ACTOR_DEV_ENV", path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Файл {path} успешно обновлен."

if __name__ == "__main__":
    mcp.run()
