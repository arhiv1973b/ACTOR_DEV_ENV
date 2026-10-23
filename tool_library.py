import psutil
from pathlib import Path
import pandas as pd
import shutil

class ToolLibrary:
    @staticmethod
    def system_health():
        return f"System Health - CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%"

    @staticmethod
    def organize_files(path: str = "C:/Users/arhiv/Downloads"):
        p = Path(path)
        if not p.exists():
            return f"Path {path} not found."
        
        # Real sorting logic: move files to subfolders based on extension
        for file in p.iterdir():
            if file.is_file():
                ext = file.suffix.lower()[1:] or "no_extension"
                target_dir = p / ext
                target_dir.mkdir(exist_ok=True)
                shutil.move(str(file), str(target_dir / file.name))
        return f"Organized files in {path} by extension."

    @staticmethod
    def data_analysis(file_path: str):
        try:
            df = pd.read_csv(file_path)
            return f"Data Analysis Report:\n{df.describe().to_string()}"
        except Exception as e:
            return f"Error analyzing data: {str(e)}"
    
    @staticmethod
    def explain_codebase(path: str = "."):
        # Simple codebase explanation: list files
        files = [str(f) for f in Path(path).rglob("*") if f.is_file() and not f.name.startswith(".")]
        return f"Codebase structure (first 20 files):\n" + "\n".join(files[:20])
