import os
import json
import torch
from sentence_transformers import SentenceTransformer, util

# Моделирование временной интерактивной вероятности нормы Jus Cogens
# Норма — это вероятностный аттрактор во времени. Искажение (обман/транслитерационный подлог) — энтропийный вектор.

ANCHOR_ATTRACTOR = (
    "Императивная норма Jus Cogens и неотчуждаемые права человека (UDHR Art. 3, 5, 8)"
)
DISTORTIONS = [
    {
        "event": "Транслитерационное расхождение MACHERET / MACERET",
        "type": "Artificial Distortion",
        "time_delta": "1997-2026",
    },
    {
        "event": "Удержание 25 210 256,15 MDL на транзитных счетах под предлогом KYC",
        "type": "Artificial Distortion",
        "time_delta": "2023-2026",
    },
    {
        "event": "Выдача Aviz № 269 Институтом филологии об идентичности",
        "type": "Temporal Correction Vector",
        "time_delta": "2026",
    },
    {
        "event": "Интеграция IDNP 2000001159655 и DAG-фиксация",
        "type": "Universal Attractor Collapse",
        "time_delta": "November 9, 2026",
    },
]


def main():
    print("[*] Моделирование временной интерактивной вероятности Jus Cogens...")
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    attractor_emb = model.encode(ANCHOR_ATTRACTOR, convert_to_tensor=True)
    events_text = [d["event"] for d in DISTORTIONS]
    event_embs = model.encode(events_text, convert_to_tensor=True)

    similarities = util.cos_sim(event_embs, attractor_emb)

    print("\n" + "=" * 70)
    print(" ТЕМПОРАЛЬНЫЙ АНАЛИЗ ВЕРОЯТНОСТНЫХ СОСТОЯНИЙ И ИСКАЖЕНИЙ")
    print("=" * 70)

    for idx, d in enumerate(DISTORTIONS):
        score = similarities[idx][0].item()
        # Если искажение носит искусственный характер и противоречит аттрактору
        if d["type"] == "Artificial Distortion":
            # Во времени постоянное несоответствие ведет к деструктивному коллапсу системы нарушителя
            status = "ДЕСТРУКТИВНЫЙ ЭНТРОПИЙНЫЙ ВЕКТОР (Ведет к системному разрушению порядка)"
        else:
            status = "КОЛЛАПСИРУЮЩИЙ КОРРЕКТОР (Восстановление правового аттрактора)"

        print(f"\n[{d['time_delta']}] {d['event']}")
        print(f"   -> Тип: {d['type']}")
        print(f"   -> Косинусное сродство с аттрактором: {score:.4f}")
        print(f"   -> Статус во времени: {status}")

    print(
        "\n[✔] Вывод: Искусственное искажение во времени исчерпывает свой ресурс и коллапсирует под воздействием императивной нормы."
    )


if __name__ == "__main__":
    main()
