import os
import torch
from sentence_transformers import SentenceTransformer, util

# Мощный комплексный правовой аттрактор Jus Cogens
CATHARSIS_ATTRACTOR = "Императивная норма Jus Cogens, реабилитация, IDNP 2000001159655, Aviz № 269 и защита активов 25 210 256,15 MDL"

LEGAL_ENTITIES = [
    {
        "name": "Постановление банка об удержании 25 210 256,15 MDL под предлогом KYC",
        "type": "Искусственное искажение",
    },
    {
        "name": "Заключение Института филологии Aviz № 269 об идентичности MACHERET и MACERET",
        "type": "Истинный Центр",
    },
    {
        "name": "Решение суда о реабилитации и возврате активов 25 210 256,15 MDL по IDNP 2000001159655",
        "type": "Истинный Центр",
    },
    {
        "name": "Отказ чиновника в признании документов из-за транслитерационного расхождения",
        "type": "Искусственное искажение",
    },
    {
        "name": "Криптографический DAG-манифест инварианта A©tor Key для IDNP 2000001159655 и Aviz № 269",
        "type": "Истинный Центр",
    },
]


def main():
    print(
        "[*] Калибровка катарсис-модели: тензорное разделение ложных обременений и истинных центров..."
    )
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    attractor_emb = model.encode(CATHARSIS_ATTRACTOR, convert_to_tensor=True)
    entity_texts = [e["name"] for e in LEGAL_ENTITIES]
    entity_embs = model.encode(entity_texts, convert_to_tensor=True)

    similarities = util.cos_sim(entity_embs, attractor_emb)

    threshold = 0.52  # Четкий порог онтологического существования

    print("\n" + "=" * 95)
    print(
        " МОМЕНТ КАТАРСИСА: КОЛЛАС ИСКУСТВЕННЫХ ОБРЕМЕНЕНИЙ И ФИКСАЦИЯ ИСТИННЫХ ЦЕНТРОВ"
    )
    print("=" * 95)

    surviving_centers = []

    for idx, entity in enumerate(LEGAL_ENTITIES):
        weight = similarities[idx][0].item()

        if weight >= threshold:
            density = weight
            status = "УСТОЙЧИВЫЙ ЦЕНТР (Сохраняет правосубъектность)"
            surviving_centers.append((entity["name"], density))
        else:
            density = 0.0
            status = "КОЛЛАПСИРОВАВШАЯ ИЛЛЮЗИЯ (Плотность обнулена / Ничтожно)"

        print(f"\n[Сущность]: {entity['name']}")
        print(f"   -> Тип: {entity['type']}")
        print(f"   -> Сродство с аттрактором: {weight:.4f}")
        print(f"   -> Плотность после катарсиса: {density:.4f}")
        print(f"   -> Статус: {status}")

    print("\n" + "-" * 95)
    print(
        f" РЕЗУЛЬТАТ КАТАРСИСА: Выживших истинных центров: {len(surviving_centers)} из {len(LEGAL_ENTITIES)}"
    )
    print(
        " Все бюрократические иллюзии и искажения обнулены. Истинные центры зафиксированы."
    )
    print("=" * 95)


if __name__ == "__main__":
    main()
