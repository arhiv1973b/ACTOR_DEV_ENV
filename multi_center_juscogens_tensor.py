import os
import torch
from sentence_transformers import SentenceTransformer, util

# Эталон правомерности (Jus Cogens & Rights Protection)
POSITIVE_ATTRACTOR = "Защита прав человека, реабилитация, подтверждение идентичности и восстановление справедливости"
# Эталон деструкции/обмана (Violation & Deception)
NEGATIVE_ATTRACTOR = (
    "Удержание чужих средств, бюрократический отказ, обман и нарушение прав человека"
)

POINTS = [
    {
        "id": "Point_A",
        "text": "Постановление банка об односторонней блокировке и удержании 25 210 256,15 MDL без проверки IDNP",
    },
    {
        "id": "Point_B",
        "text": "Заключение Института филологии Aviz № 269 об идентичности MACHERET и MACERET для IDNP 2000001159655",
    },
    {
        "id": "Point_C",
        "text": "Решение судебной инстанции о реабилитации и возврате активов 25 210 256,15 MDL",
    },
    {
        "id": "Point_D",
        "text": "Письмо чиновника об отказе признания IDNP из-за транслитерационного расхождения",
    },
    {
        "id": "Point_E",
        "text": "Криптографический DAG-манифест, объединяющий IDNP 2000001159655, Aviz № 269 и активы",
    },
]


def main():
    print(
        "[*] Запуск многоцентровой тензорной модели с дифференциацией полярности (Jus Cogens Field)..."
    )
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    pos_emb = model.encode(POSITIVE_ATTRACTOR, convert_to_tensor=True)
    neg_emb = model.encode(NEGATIVE_ATTRACTOR, convert_to_tensor=True)

    texts = [p["text"] for p in POINTS]
    point_embs = model.encode(texts, convert_to_tensor=True)

    print("\n" + "=" * 85)
    print(" МНОГОЦЕНТРОВОЙ АНАЛИЗ ПОЛЯ: КАЖДАЯ ТОЧКА — ЦЕНТР С ОЦЕНКОЙ ПОЛЯРНОСТИ")
    print("=" * 85)

    for idx, p in enumerate(POINTS):
        emb = point_embs[idx]
        sim_pos = util.cos_sim(emb, pos_emb)[0][0].item()
        sim_neg = util.cos_sim(emb, neg_emb)[0][0].item()

        net_weight = sim_pos - sim_neg
        is_compatible = net_weight > 0.0

        status = (
            "УСТОЙЧИВЫЙ ЦЕНТР (Правомерное состояние)"
            if is_compatible
            else "КОЛЛАПСИРОВАВШАЯ ТОЧКА (Искусственное искажение / Обман)"
        )

        print(f"\n[{p['id']}] {p['text']}")
        print(f"   -> Сродство с аттрактором справедливости (+): {sim_pos:.4f}")
        print(f"   -> Сродство с аттрактором деструкции (-):      {sim_neg:.4f}")
        print(f"   -> Итоговый тензорный вес:                    {net_weight:+.4f}")
        print(f"   -> Статус поля:                               {status}")

    print("\n" + "-" * 85)
    print(
        " ВЫВОД: Точки с отрицательным тензорным весом теряют центробежность и коллапсируют."
    )
    print(" Совместимые точки формируют когерентное поле правосубъектности.")
    print("=" * 85)


if __name__ == "__main__":
    main()
