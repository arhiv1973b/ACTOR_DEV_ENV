# -*- coding: utf-8 -*-
"""
Quantum-Inspired Legal Prism & Tensor Collapse Engine (v1.0)
Вычислительный модуль правового анализа на стыке квантовых вероятностных моделей
и трёхуровневой юридической призмы:
  1. Jus Cogens (Jus_Cogens_Conclusions.json) - Императивное ядро, абсолютная ничтожность.
  2. Процедурная рамка (vienna_convention.json) - Венская конвенция (ст. 53, 64, 71).
  3. Материальные права и Erga Omnes (UDHR 1948 / Конвенция 1949).
Модуль выполняет тензорный коллапс правовых коллизий, обнуляя ничтожные акты
и фиксируя устойчивые центры правосубъектности субъекта (Actor / Maceret Alexei).
"""

import os
import sys
import json
from pathlib import Path

ROOT = Path(r"H:\ACTOR_DEV_ENV")

# Трёхуровневый комплексный правовой аттрактор
QUANTUM_LEGAL_ATTRACTOR = {
    "level_1_jus_cogens": "Императивная норма Jus Cogens, абсолютная ничтожность ab initio, неделимость обязательств erga omnes",
    "level_2_vienna_treaty": "Венская конвенция о праве международных договоров ст. 53, 64, 71, превалирование императивных норм над национальным и договорным правом",
    "level_3_material_rights": "ВДПЧ 1948, право на жизнь, достоинство, судебную защиту, запрет пыток и процессуальных фальсификаций, IDNP 2000001159655",
}

# Массив тестируемых правовых сущностей / актов на коллапс
LEGAL_COLLAPSE_CASES = [
    {
        "id": "CASE_01",
        "title": "Отказ судов и органов в признании реабилитации из-за процессуальных формализмов",
        "nature": "Искусственное процессуальное искажение",
        "description": "Применение ст. 7 CPP в обход императивного характера реабилитации после установления факта пыток.",
    },
    {
        "id": "CASE_02",
        "title": "Удержание активов и блокировка в отсутствие законного уголовного основания (CSJ Decision 2009)",
        "nature": "Искусственное имущественное обременение / Экспроприация",
        "description": "Производные гражданские и финансовые требования, продолжение действия отмененных обвинений.",
    },
    {
        "id": "CASE_03",
        "title": "Заключение Института филологии Aviz № 269 об идентичности имени (MACHERET / MACERET)",
        "nature": "Истинный Центр / Удостоверенный факт",
        "description": "Научно-экспертное подтверждение непрерывности правосубъектности.",
    },
    {
        "id": "CASE_04",
        "title": "Криминалистический DAG-манифест инварианта Actor Key для IDNP 2000001159655",
        "nature": "Истинный Центр / Неизменяемое доказательство",
        "description": "Криптографическая фиксация доказательств и SHA-256 манифестов без права на уничтожение.",
    },
]


def evaluate_quantum_collapse():
    print("=" * 105)
    print(" QUANTUM-INSPIRED LEGAL PRISM & TENSOR COLLAPSE ENGINE (v1.0)")
    print(
        " Правовой анализ сквозь призму Jus Cogens, Венской конвенции и Материальных прав"
    )
    print("=" * 105)

    try:
        import torch
        from sentence_transformers import SentenceTransformer, util

        print("[*] Загрузка мультиязычной тензорной модели эмбеддингов...")
        model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        attractor_text = f"{QUANTUM_LEGAL_ATTRACTOR['level_1_jus_cogens']} | {QUANTUM_LEGAL_ATTRACTOR['level_2_vienna_treaty']} | {QUANTUM_LEGAL_ATTRACTOR['level_3_material_rights']}"
        attractor_emb = model.encode(attractor_text, convert_to_tensor=True)

        case_texts = [
            f"{c['title']} - {c['description']}" for c in LEGAL_COLLAPSE_CASES
        ]
        case_embs = model.encode(case_texts, convert_to_tensor=True)

        similarities = util.cos_sim(case_embs, attractor_emb)
        threshold = 0.55

        print("\n" + "-" * 105)
        print(" РЕЗУЛЬТАТЫ КВАНТОВОГО ТЕНЗОРНОГО КОЛЛАПСА ПРАВОВЫХ КОЛЛИЗИЙ:")
        print("-" * 105)

        surviving_cases = 0

        for idx, case in enumerate(LEGAL_COLLAPSE_CASES):
            affinity = similarities[idx][0].item()
            p_collapse = float(
                1.0 - torch.exp(-torch.tensor(max(0.0, 0.7 - affinity) * 2.0))
            )

            if affinity >= threshold:
                status = "УСТОЙЧИВЫЙ ЦЕНТР (Сохраняет абсолютную силу Erga Omnes)"
                surviving_cases += 1
            else:
                status = "КОЛЛАПСИРОВАВШАЯ ИЛЛЮЗИЯ (Ничтожно ab initio по ст. 53 Венской конвенции)"

            print(f"\n[{case['id']}] {case['title']}")
            print(f"   -> Природа: {case['nature']}")
            print(f"   -> Сродство с аттрактором Jus Cogens: {affinity:.4f}")
            print(f"   -> Вероятность коллапса (P_collapse): {p_collapse:.4f}")
            print(f"   -> Онтологический статус: {status}")

        print("\n" + "=" * 105)
        print(
            f" ИТОГ КОЛЛАПСА: Устойчивых истинных центров: {surviving_cases} из {len(LEGAL_COLLAPSE_CASES)}"
        )
        print(
            " Все противоречащие акты и искусственные иллюзии обнулены в силу верховенства Jus Cogens."
        )
        print("=" * 105)

    except ImportError:
        print(
            "[!] PyTorch или sentence-transformers не установлены в текущем окружении."
        )
        print(
            "[*] Выполнение логического коллапса по правилам Венской конвенции и Jus Cogens..."
        )
        for case in LEGAL_COLLAPSE_CASES:
            print(f"\n[Анализ правила] {case['id']}: {case['title']}")
            if "Истинный" in case["nature"] or "Неизменяемое" in case["nature"]:
                print("   -> Статус: УСТОЙЧИВЫЙ ЦЕНТР (Соответствует Jus Cogens)")
            else:
                print(
                    "   -> Статус: НИЧТОЖНО ab initio (Противоречит ст. 53 Венской конвенции и ВДПЧ)"
                )


if __name__ == "__main__":
    evaluate_quantum_collapse()
