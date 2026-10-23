import hashlib
import os

files = [
    (
        r"H:\ACTOR_DEV_ENV\evidence_vault\Документ (3) (8).pdf",
        "UDHR Art. 17.2 — Произвольное лишение имущества",
        "DIRECT VIOLATION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\inbox\emails\email_01_arrest_1997.txt",
        "UDHR Art. 3 — Право на свободу и личную неприкосновенность",
        "CONTINUING VIOLATION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\inbox\emails\email_02_evidence.txt",
        "UDHR Art. 17.2 — Защита права собственности",
        "SUPPORTING EVIDENCE",
    ),
    (
        r"H:\ACTOR_DEV_ENV\evidence_vault\procuratura_riscani_refusal_17092026.txt",
        "UDHR Art. 8 / 17.2 — Отказ в правовой защите (Прокуратура Рышкань, 17.09.2026)",
        "OFFICIAL OBSTRUCTION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\evidence_vault\police_riscani_closure_24092026.txt",
        "UDHR Art. 8 / 17.2 — Прекращение производства (ИП Рышкань, 24.09.2026)",
        "OFFICIAL OBSTRUCTION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\maceret-case-evidence\udhr_claim_manifest.json",
        "UDHR Art. 17.2 — Манифест требований ВДПЧ",
        "DIRECT VIOLATION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\dag_manifest.json",
        "UDHR Art. 17.2 — Криптографический DAG-манифест",
        "DIRECT VIOLATION",
    ),
]

print("# Updated Evidence Index Summary (CASE-MACHERET-1997-2026)\n")
print("| Filename | SHA-256 | UDHR Binding | Relation |")
print("|---|---|---|---|")

for path, udhr, relation in files:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        sha = h.hexdigest()
    except Exception as e:
        sha = f"ERROR: {e}"
    filename = os.path.basename(path)
    print(f"| {filename} | `{sha}` | {udhr} | {relation} |")
