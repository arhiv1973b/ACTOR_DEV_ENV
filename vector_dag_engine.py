import os
import json
import torch
from sentence_transformers import SentenceTransformer, util

MANIFEST_PATH = r"H:\ACTOR_DEV_ENV\dag_manifest.json"


def main():
    print("[*] Загрузка DAG-манифеста...")
    if not os.path.exists(MANIFEST_PATH):
        print(f"Манифест не найден: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        entries = data.get("entries", [])

    print(f"[*] Загружено записей из DAG: {len(entries)}")

    # Сбор документов и их метаданных для векторизации
    documents = []
    metadata_records = []

    for idx, entry in enumerate(entries):
        # Извлекаем тексты из payload илиfilename
        payload = entry.get("payload", {})
        filename = (
            entry.get("filename") or payload.get("document_ref") or f"Entry_{idx}"
        )
        summary = (
            payload.get("summary")
            or payload.get("case_id")
            or "Юридический документ / доказательство"
        )

        doc_text = f"Файл: {filename}. Описание: {summary}."
        if "findings" in payload:
            findings = payload["findings"]
            if isinstance(findings, dict):
                fraud = ", ".join(findings.get("fraud_type", []))
                amt = findings.get("financial_impact_mdl", "")
                doc_text += f" Нарушения: {fraud}. Сумма: {amt} MDL."

        documents.append(doc_text)
        metadata_records.append(
            {
                "index": idx,
                "filename": filename,
                "summary": summary,
                "node_hash": entry.get("node_hash", "")[:16],
            }
        )

    print(
        "[*] Инициализация модели эмбеддингов (paraphrase-multilingual-MiniLM-L12-v2)..."
    )
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("[*] Генерация векторных эмбеддингов для документов DAG...")
    embeddings = model.encode(documents, convert_to_tensor=True, show_progress_bar=True)

    # Примеры семантических запросов
    queries = [
        "Дело о 25 миллионах леев и мошенничестве",
        "Уведомление о выявлении нарушений и подлоге",
        "Судебная реабилитация и устранение коллизий",
    ]

    print("\n" + "=" * 60)
    print(" РЕЗУЛЬТАТЫ СЕМАНТИЧЕСКОГО ПОИСКА ПО DAG-МАТРИЦЕ")
    print("=" * 60)

    for query in queries:
        print(f"\n🔍 Запрос: «{query}»")
        query_embedding = model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, embeddings)[0]

        # Топ-3 результата
        top_results = torch.topk(cos_scores, k=min(3, len(documents)))
        for score, idx in zip(top_results.values, top_results.indices):
            rec = metadata_records[idx.item()]
            print(
                f"   -> Сходство: {score.item():.4f} | Файл: {rec['filename']} | Хэш: {rec['node_hash']}..."
            )
            print(f"      Суммаризация: {rec['summary']}")

    print("\n[✔] Векторный анализ и индексация DAG-матрицы успешно завершены.")


if __name__ == "__main__":
    main()
