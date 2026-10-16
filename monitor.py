from mcp_drive_indexer import DatabaseManager

db = DatabaseManager("drive_index.db")
with db.get_connection() as conn:
    stats = dict(conn.execute("SELECT status, COUNT(*) FROM files GROUP BY status").fetchall())
    active = conn.execute("SELECT path FROM files WHERE status = \"PROCESSING\" LIMIT 5").fetchall()
    errors = conn.execute("SELECT path FROM files WHERE status = \"FAILED\" LIMIT 5").fetchall()

print(f"\n[📊 Статистика очереди]: {stats}")
print("\n[⏳ В работе (PROCESSING)]:")
if active:
    for r in active: print(f"  -> {r[0]}")
else:
    print("  (нет активных потоков прямо сейчас)")

print("\n[❌ Ошибки (FAILED)]:")
if errors:
    for r in errors: print(f"  [!] {r[0]}")
else:
    print("  (ошибок нет, все файлы обрабатываются корректно)")
