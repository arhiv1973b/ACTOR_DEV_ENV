import json
from datetime import datetime, timezone

matrix_data = {
    "project_id": "CASE-MACHERET-1997-2026",
    "legal_frameworks": [
        "Global Magnitsky Act",
        "ECHR Art. 3, 5, 13",
        "UDHR Jus Cogens",
    ],
    "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "targets": [
        {
            "entity_id": "TARGET-001",
            "name": "[Имя Фамилия/Должность Фигуранта 1]",
            "role": "Ликвидатор / Должностное лицо банка / Прокурор",
            "violations": [
                "Саботаж возврата финансовых активов",
                "Соучастие в легализации последствий незаконного задержания (continuing consequences)",
            ],
            "evidence_refs": ["v2026.09.03-audit", "hash_technology_test_report.json"],
            "proposed_sanction": "OFAC Asset Freeze & Visa Ban",
        }
    ],
    "international_petitions_status": {
        "us_treasury_ofac": "pending_draft",
        "echr_rule_39": "pending_draft",
        "eu_council": "pending_draft",
    },
}

with open("international_sanctions_matrix.json", "w", encoding="utf-8") as f:
    json.dump(matrix_data, f, indent=4, ensure_ascii=False)

print(
    "✅ Матрица международных санкций (international_sanctions_matrix.json) инициализирована."
)
