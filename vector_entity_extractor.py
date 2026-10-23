import os
import json
import re
import torch
from sentence_transformers import SentenceTransformer, util

MANIFEST_PATH = r"H:\ACTOR_DEV_ENV\dag_manifest.json"
REPORT_PATH = r"H:\ACTOR_DEV_ENV\VECTOR_ENTITY_EXTRACTION_REPORT.json"

# Регулярные выражения для извлечения юридических сущностей
IDNP_REGEX = re.compile(r"\b\d{13}\b")
AMOUNT_REGEX = re.compile(
    r"\b\d{1,3}(?:\s\d{3})*(?:[,.]\d{2})?\s*(?:MDL|лей|lei)\b", re.IGNORECASE
)
AVIZ_REGEX = re.compile(r"(?:Aviz|Авиз|Заключение)\s*(?:№|nr\.?)?\s*\d+", re.IGNORECASE)
COURT_REGEX = re.compile(
    r"(?:Суд|Judecătoria|Трибунал|Коллегия)\s+[А-Яа-яA-Za-z\s–-]+", re.IGNORECASE
)


def extract_entities(text):
    idnp_found = list(set(IDNP_REGEX.findall(text)))
    amounts_found = list(set(AMOUNT_REGEX.findall(text)))
    aviz_found = list(set(AVIZ_REGEX.findall(text)))
    courts_found = list(set(COURT_REGEX.findall(text)))

    return {
        "idnp": idnp_found,
        "amounts": amounts_found,
        "aviz": aviz_found,
        "courts": courts_found,
    }


def main():
    print("[*] Загрузка DAG-манифеста для извлечения сущностей...")
    if not os.path.exists(MANIFEST_PATH):
        print(f"Манифест не найден: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        entries = data.get("entries", [])

    print(f"[*] Обработка {len(entries)} записей DAG и извлечение сущностей...")

    documents = []
    extracted_records = []

    for idx, entry in enumerate(entries):
        payload = entry.get("payload", {})
        filename = (
            entry.get("filename") or payload.get("document_ref") or f"Entry_{idx}"
        )
        summary = payload.get("summary") or payload.get("case_id") or ""

        # Полный текст для анализа и эмбеддингов
        full_text = f"Файл: {filename}. Описание: {summary}."
        if "findings" in payload:
            findings = payload["findings"]
            if isinstance(findings, dict):
                full_text += f" Данные: {json.dumps(findings, ensure_ascii=False)}"

        # Извлекаем сущности
        entities = extract_entities(full_text)

        documents.append(full_text)
        extracted_records.append(
            {
                "index": idx,
                "filename": filename,
                "node_hash": entry.get("node_hash", ""),
                "summary": summary,
                "extracted_entities": entities,
                "payload_snapshot": payload,
            }
        )

    print("[*] Инициализация модели эмбеддингов...")
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    embeddings = model.encode(
        documents, convert_to_tensor=True, show_progress_bar=False
    )

    # Пример автоматического векторного поиска с группировкой по извлеченным сущностям
    test_queries = [
        "Дело о 25 миллионах леев",
        "Уведомление о мошенничестве",
        "Судебная реабилитация",
    ]

    print("\n" + "=" * 60)
    print(" РЕЗУЛЬТАТЫ АВТОМАТИЧЕСКОГО ИЗВЛЕЧЕНИЯ СУЩНОСТЕЙ И ПОИСКА")
    print("=" * 60)

    results_summary = []
    for q in test_queries:
        q_emb = model.encode(q, convert_to_tensor=True)
        scores = util.cos_sim(q_emb, embeddings)[0]
        top_res = torch.topk(scores, k=min(2, len(documents)))

        print(f"\n🔍 Запрос: «{q}»")
        for score, idx in zip(top_res.values, top_res.indices):
            rec = extracted_records[idx.item()]
            print(f"   -> Сходство: {score.item():.4f} | Файл: {rec['filename']}")
            print(
                f"      Сущности: IDNP: {rec['extracted_entities']['idnp']} | Суммы: {rec['extracted_entities']['amounts']} | Авиз: {rec['extracted_entities']['aviz']}"
            )
            results_summary.append(
                {
                    "query": q,
                    "score": score.item(),
                    "filename": rec["filename"],
                    "entities": rec["extracted_entities"],
                }
            )

    # Сохраняем отчет с извлеченными сущностями
    output_report = {
        "total_entries_processed": len(extracted_records),
        "extracted_records": extracted_records,
        "search_samples": results_summary,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(output_report, f, ensure_ascii=False, indent=4)

    print(f"\n[✔] Отчет с извлеченными сущностями успешно сохранен в {REPORT_PATH}")


if __name__ == "__main__":
    main()
