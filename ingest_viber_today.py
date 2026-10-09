import os
import hashlib
import json
from datetime import datetime, timezone

viber_dir = r"C:\Users\arhiv\OneDrive\Документы\ViberDownloads"
results = []

if os.path.exists(viber_dir):
    for filename in os.listdir(viber_dir):
        path = os.path.join(viber_dir, filename)
        if os.path.isfile(path):
            try:
                mtime = os.path.getmtime(path)
                mtime_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
                # Check if modified today (UTC date or local date comparison)
                # Let's compare date string YYYY-MM-DD
                today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                file_date_str = mtime_dt.strftime("%Y-%m-%d")

                # Also include files modified on 2026-10-09
                if file_date_str == "2026-10-09":
                    sha256 = hashlib.sha256()
                    with open(path, "rb") as f:
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            sha256.update(chunk)
                    results.append(
                        {
                            "filename": filename,
                            "path": path,
                            "size_bytes": os.path.getsize(path),
                            "sha256": sha256.hexdigest(),
                            "last_modified": mtime_dt.isoformat(),
                            "status": "processed_today",
                        }
                    )
            except Exception as e:
                results.append(
                    {
                        "filename": filename,
                        "path": path,
                        "error": str(e),
                        "status": "error",
                    }
                )

manifest = {
    "manifest_schema": "TI-ULA/1.0",
    "target_directory": viber_dir,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "processed_count": len(results),
    "evidence_items": results,
}

output_path = (
    r"H:\ACTOR_DEV_ENV\artifacts\reabilitare\VIBER_TODAY_MANIFEST_20261009.json"
)
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(
    f"Successfully processed {len(results)} files modified today. Manifest saved to {output_path}"
)
