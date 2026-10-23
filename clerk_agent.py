import sys, time, argparse, hashlib, json, os, shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ClerkHandler(FileSystemEventHandler):
    def __init__(self, dest_path, log_path):
        self.dest_path = dest_path
        self.log_path = log_path
        self.keywords = ["ordonanță", "încheiere", "cerere", "decizie", "recurs"]

    def on_created(self, event):
        if not event.is_directory:
            print(f"[A©t0r] Обнаружен: {event.src_path}")
            self.classify_and_move(event.src_path)

    def classify_and_move(self, filepath):
        filename = os.path.basename(filepath).lower()
        category = "General"
        for kw in self.keywords:
            if kw in filename:
                category = kw.capitalize()
                break
        
        target_dir = os.path.join(self.dest_path, category)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, os.path.basename(filepath))
        
        try:
            with open(filepath, "rb") as f: file_hash = hashlib.sha256(f.read()).hexdigest()
            shutil.move(filepath, target_path)
            entry = {"timestamp": time.time(), "file": target_path, "sha256": file_hash, "category": category}
            with open(self.log_path, "a", encoding="utf-8") as f: f.write(json.dumps(entry) + "\n")
            print(f"[A©t0r] Классифицирован: {category} -> {file_hash[:16]}...")
        except Exception as e: print(f"[!] Ошибка: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", required=True); parser.add_argument("--dest", required=True); parser.add_argument("--log", required=True)
    args = parser.parse_args()
    observer = Observer()
    observer.schedule(ClerkHandler(args.dest, args.log), args.watch, recursive=False)
    print(f"[A©t0r Protocol] Клерк Classifier активен. Мониторинг: {args.watch}")
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()
