import os
from datetime import datetime


def main():
    archive_dir = os.path.abspath("apostille-mirror/logs/archive")
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    logs = []
    for f in sorted(os.listdir(archive_dir)):
        if f.endswith(".log"):
            filepath = os.path.join(archive_dir, f)
            stat = os.stat(filepath)
            logs.append(
                {
                    "filename": f,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

    index_html = f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<title>Swarm Deployment Logs Archive Index</title>
<style>
  body {{ background: #050a0f; color: #c0d8ec; font-family: 'Share Tech Mono', monospace, sans-serif; padding: 25px; line-height: 1.6; }}
  h1 {{ color: #f0c040; border-bottom: 1px solid #103c60; padding-bottom: 10px; }}
  input[type="text"] {{ width: 100%; padding: 10px; background: #071220; border: 1px solid #0c2e4a; color: #40d4ff; border-radius: 4px; margin-bottom: 20px; font-size: 1rem; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ margin: 10px 0; background: #071220; padding: 12px; border: 1px solid #0c2e4a; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }}
  a {{ color: #40d4ff; text-decoration: none; font-weight: bold; }}
  a:hover {{ text-decoration: underline; }}
  .meta {{ color: #00b8e8; font-size: 0.9rem; }}
</style>
</head>
<body>
  <h1>📁 Swarm Logs Archive Index</h1>
  <p>Generated at: {datetime.now().isoformat()}</p>
  <input type="text" id="searchInput" placeholder="Search logs by filename or timestamp..." onkeyup="filterLogs()">
  <ul id="logList">
"""

    for log in logs:
        index_html += f"""    <li data-filename="{log["filename"].lower()}">
      <a href="{log["filename"]}">{log["filename"]}</a>
      <span class="meta">Size: {log["size"]} bytes | Date: {log["modified"]}</span>
    </li>
"""

    index_html += """  </ul>

  <script>
    function filterLogs() {
      let input = document.getElementById('searchInput').value.toLowerCase();
      let list = document.getElementById('logList');
      let items = list.getElementsByTagName('li');
      for (let i = 0; i < items.length; i++) {
        let filename = items[i].getAttribute('data-filename');
        if (filename.indexOf(input) > -1) {
          items[i].style.display = "";
        } else {
          items[i].style.display = "none";
        }
      }
    }
  </script>
</body>
</html>
"""

    out_path = os.path.join(archive_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"[Archive Index] Updated archive index with JS search at {out_path}")


if __name__ == "__main__":
    main()
