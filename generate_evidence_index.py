import hashlib
import os

files = [
    (
        r"H:\ACTOR_DEV_ENV\evidence_vault\Документ (3) (8).pdf",
        "UDHR Art. 17.2 — Никто не должен быть произвольно лишен своего имущества",
        "DIRECT VIOLATION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\inbox\emails\email_01_arrest_1997.txt",
        "UDHR Art. 3 — Право на жизнь, свободу и личную неприкосновенность",
        "CONTINUING VIOLATION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\inbox\emails\email_02_evidence.txt",
        "UDHR Art. 17.2 — Никто не должен быть произвольно лишен своего имущества",
        "SUPPORTING EVIDENCE",
    ),
    (
        r"H:\ACTOR_DEV_ENV\maceret-case-evidence\udhr_claim_manifest.json",
        "UDHR Art. 17.2 — Никто не должен быть произвольно лишен своего имущества",
        "DIRECT VIOLATION",
    ),
    (
        r"H:\ACTOR_DEV_ENV\dag_manifest.json",
        "UDHR Art. 17.2 — Никто не должен быть произвольно лишен своего имущества",
        "DIRECT VIOLATION",
    ),
]

print("# Evidence Index Summary (CASE-MACHERET-1997-2026)\n")
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
