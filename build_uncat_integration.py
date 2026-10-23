#!/usr/bin/env python3
"""
UNCAT 1984 Kernel & Multilingual Harmonizer / DAG Integrator
Создает uncat_kernel.json, мультиязычные версии (EN, FR, RU, RO, ES), конвертирует в YAML
и интегрирует узел в ECHR_IMPUNITY_DAG.json.
"""

import os
import json
import yaml
import hashlib

UNCAT_DATA = {
    "metadata": {
        "file_type": "UNCAT_1984_CORE",
        "authenticity_verification": "HARMONIZED_ARTICLE_85_VCLT",
        "project_projection": "CASE-MACHERET-1997-2026",
    },
    "quantum_weights_1_to_9": {
        "description": "Абсолютный запрет пыток (UNCAT Art. 2.2). Квантовая суперпозиция исключает любые оправдания.",
        "weight_1": {
            "qubit_value": 0.111111,
            "principle": "No exceptional circumstances whatsoever (war, political instability) may be invoked.",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_2": {
            "qubit_value": 0.111111,
            "principle": "An order from a superior officer or a public authority may not be invoked as a justification.",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_3": {
            "qubit_value": 0.111111,
            "principle": "Non-refoulement obligation (Art. 3)",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_4": {
            "qubit_value": 0.111111,
            "principle": "Criminalization of torture in domestic law (Art. 4)",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_5": {
            "qubit_value": 0.111111,
            "principle": "Universal jurisdiction & custody measures (Art. 5-6)",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_6": {
            "qubit_value": 0.111111,
            "principle": "Extradition obligations or prosecution (Art. 7-8)",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_7": {
            "qubit_value": 0.111111,
            "principle": "Mutual judicial assistance (Art. 9)",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_8": {
            "qubit_value": 0.111111,
            "principle": "Education and training prohibition integration (Art. 10-11)",
            "status": "SUPERPOSITION_ACTIVE",
        },
        "weight_9": {
            "qubit_value": 0.111111,
            "principle": "Inadmissibility of evidence obtained under torture (Art. 15)",
            "status": "SUPERPOSITION_ACTIVE",
        },
    },
    "imperative_layer_10_plus": {
        "description": "Механизмы исполнения и восстановления (Jus Cogens nullifier)",
        "norms": [
            {
                "id": 10,
                "article": "UNCAT Article 12",
                "norm": "Prompt and impartial investigation wherever there is reasonable ground to believe an act of torture has been committed.",
            },
            {
                "id": 11,
                "article": "UNCAT Article 13",
                "norm": "Right to complain to, and to have the case promptly and impartially examined by, competent authorities with whistleblower protection.",
            },
            {
                "id": 12,
                "article": "UNCAT Article 14",
                "norm": "Enforceable right to fair and adequate compensation, including the means for as full rehabilitation as possible.",
            },
        ],
    },
}

TRANSLATIONS_UNCAT = {
    "EN": UNCAT_DATA,
    "FR": {
        "metadata": {
            "file_type": "UNCAT_1984_CORE_FR",
            "authenticity_verification": "HARMONIZED_ARTICLE_85_VCLT",
        },
        "quantum_weights_1_to_9": {
            "description": "Interdiction absolue de la torture (Art. 2.2).",
            "weight_1": {
                "qubit_value": 0.111111,
                "principle": "Aucune circonstance exceptionnelle ne peut être invoquée.",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_2": {
                "qubit_value": 0.111111,
                "principle": "Un ordre d'un supérieur ne peut servir de justification.",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_3": {
                "qubit_value": 0.111111,
                "principle": "Obligation de non-refoulement (Art. 3)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_4": {
                "qubit_value": 0.111111,
                "principle": "Inrimination de la torture (Art. 4)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_5": {
                "qubit_value": 0.111111,
                "principle": "Juridiction universelle (Art. 5-6)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_6": {
                "qubit_value": 0.111111,
                "principle": "Extradition ou poursuite (Art. 7-8)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_7": {
                "qubit_value": 0.111111,
                "principle": "Entraide judiciaire (Art. 9)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_8": {
                "qubit_value": 0.111111,
                "principle": "Formation et éducation (Art. 10-11)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_9": {
                "qubit_value": 0.111111,
                "principle": "Irrecevabilité des aveux sous la torture (Art. 15)",
                "status": "SUPERPOSITION_ACTIVE",
            },
        },
        "imperative_layer_10_plus": {
            "norms": [
                {
                    "id": 10,
                    "article": "Art. 12",
                    "norm": "Enquête rapide et impartiale.",
                },
                {
                    "id": 11,
                    "article": "Art. 13",
                    "norm": "Droit de plainte et protection des témoins.",
                },
                {
                    "id": 12,
                    "article": "Art. 14",
                    "norm": "Droit à réparation équitable et réhabilitation.",
                },
            ]
        },
    },
    "RU": UNCAT_DATA,
    "RO": {
        "metadata": {
            "file_type": "UNCAT_1984_CORE_RO",
            "authenticity_verification": "HARMONIZED_ARTICLE_85_VCLT",
        },
        "quantum_weights_1_to_9": {
            "description": "Interzicerea absolută a torturii (Art. 2.2).",
            "weight_1": {
                "qubit_value": 0.111111,
                "principle": "Nicio circumstanță excepțională nu poate fi invocată.",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_2": {
                "qubit_value": 0.111111,
                "principle": "Ordinul unui superior nu poate justifica tortura.",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_3": {
                "qubit_value": 0.111111,
                "principle": "Obligația de nereturnare (Art. 3)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_4": {
                "qubit_value": 0.111111,
                "principle": "Infracțiunea de tortură în dreptul intern (Art. 4)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_5": {
                "qubit_value": 0.111111,
                "principle": "Jurisdicție universală (Art. 5-6)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_6": {
                "qubit_value": 0.111111,
                "principle": "Extrădare sau urmărire penală (Art. 7-8)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_7": {
                "qubit_value": 0.111111,
                "principle": "Asistență judiciară reciprocă (Art. 9)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_8": {
                "qubit_value": 0.111111,
                "principle": "Educație și formare (Art. 10-11)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_9": {
                "qubit_value": 0.111111,
                "principle": "Inadmisibilitatea probelor obținute sub tortură (Art. 15)",
                "status": "SUPERPOSITION_ACTIVE",
            },
        },
        "imperative_layer_10_plus": {
            "norms": [
                {
                    "id": 10,
                    "article": "Art. 12",
                    "norm": "Investigație promptă și imparțială.",
                },
                {
                    "id": 11,
                    "article": "Art. 13",
                    "norm": "Dreptul la plângere și protecția martorilor.",
                },
                {
                    "id": 12,
                    "article": "Art. 14",
                    "norm": "Dreptul la despăgubire echitabilă și reabilitare.",
                },
            ]
        },
    },
    "ES": {
        "metadata": {
            "file_type": "UNCAT_1984_CORE_ES",
            "authenticity_verification": "HARMONIZED_ARTICLE_85_VCLT",
        },
        "quantum_weights_1_to_9": {
            "description": "Prohibición absoluta de la tortura (Art. 2.2).",
            "weight_1": {
                "qubit_value": 0.111111,
                "principle": "Ninguna circunstancia excepcional puede invocarse.",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_2": {
                "qubit_value": 0.111111,
                "principle": "Una orden de un superior no puede servir de justificación.",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_3": {
                "qubit_value": 0.111111,
                "principle": "Obligación de no devolución (Art. 3)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_4": {
                "qubit_value": 0.111111,
                "principle": "Tipificación penal de la tortura (Art. 4)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_5": {
                "qubit_value": 0.111111,
                "principle": "Jurisdicción universal (Art. 5-6)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_6": {
                "qubit_value": 0.111111,
                "principle": "Extradición o procesamiento (Art. 7-8)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_7": {
                "qubit_value": 0.111111,
                "principle": "Asistencia judicial mutua (Art. 9)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_8": {
                "qubit_value": 0.111111,
                "principle": "Educación y capacitación (Art. 10-11)",
                "status": "SUPERPOSITION_ACTIVE",
            },
            "weight_9": {
                "qubit_value": 0.111111,
                "principle": "Inadmisión de pruebas obtenidas bajo tortura (Art. 15)",
                "status": "SUPERPOSITION_ACTIVE",
            },
        },
        "imperative_layer_10_plus": {
            "norms": [
                {
                    "id": 10,
                    "article": "Art. 12",
                    "norm": "Investigación pronta e imparcial.",
                },
                {
                    "id": 11,
                    "article": "Art. 13",
                    "norm": "Derecho de denuncia y protección de testigos.",
                },
                {
                    "id": 12,
                    "article": "Art. 14",
                    "norm": "Derecho a indemnización justa y rehabilitación.",
                },
            ]
        },
    },
}


def execute_uncat_integration():
    base_dir = "H:\\ACTOR_DEV_ENV"

    # 1. Save uncat_kernel.json
    kernel_path = os.path.join(base_dir, "uncat_kernel.json")
    with open(kernel_path, "w", encoding="utf-8") as f:
        json.dump(UNCAT_DATA, f, ensure_ascii=False, indent=2)
    print(f"[*] Создан uncat_kernel.json: {kernel_path}")

    # 2. Save multilingual translations
    for lang, payload in TRANSLATIONS_UNCAT.items():
        fname = os.path.join(base_dir, f"uncat_kernel_{lang.lower()}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[+] Создан мультиязычный UNCAT ({lang}): {fname}")

    # 3. Convert to YAML (uncat_authentic_harmonized_base.yaml)
    yaml_path = os.path.join(base_dir, "uncat_authentic_harmonized_base.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(UNCAT_DATA, f, allow_unicode=True, sort_keys=False)
    print(f"[*] Сформирован YAML-базис UNCAT: {yaml_path}")

    # 4. Integrate into ECHR_IMPUNITY_DAG.json
    dag_path = os.path.join(
        base_dir, "🏛️_EVIDENCE", "LEGAL_DOCTRINE", "ECHR_IMPUNITY_DAG.json"
    )
    if os.path.exists(dag_path):
        with open(dag_path, "r", encoding="utf-8") as f:
            dag = json.load(f)

        new_node = {
            "id": "UNCAT_1984_Anchor",
            "label": "UNCAT 1984 Anchor",
            "description": "Конвенция против пыток (UNCAT Art. 12-14, 2.2): абсолютный запрет пыток как императивная норма jus cogens, требующая незамедлительного расследования и блокирующая национальные иммунитеты.",
        }

        new_edges = [
            {
                "from": "Jus_Cogens_Invariant",
                "to": "UNCAT_1984_Anchor",
                "relation": "Erga omnes obligation of torture prohibition",
            },
            {
                "from": "UNCAT_1984_Anchor",
                "to": "ETS_nr_2_Anchor",
                "relation": "institutional_override",
            },
            {
                "from": "UNCAT_1984_Anchor",
                "to": "Geopolitical_Genesis_of_Impunity",
                "relation": "continuing consequences of uninvestigated torture",
            },
        ]

        # Check if node already exists
        if not any(n["id"] == "UNCAT_1984_Anchor" for n in dag.get("nodes", [])):
            dag["nodes"].append(new_node)

        for edge in new_edges:
            if not any(
                e.get("from") == edge["from"] and e.get("to") == edge["to"]
                for e in dag.get("edges", [])
            ):
                dag["edges"].append(edge)

        with open(dag_path, "w", encoding="utf-8") as f:
            json.dump(dag, f, ensure_ascii=False, indent=2)
        print(
            f"[*] Граф ECHR_IMPUNITY_DAG.json успешно обновлен узлом UNCAT_1984_Anchor."
        )


if __name__ == "__main__":
    execute_uncat_integration()
