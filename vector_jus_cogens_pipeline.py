import os
import torch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from sentence_transformers import SentenceTransformer, util

# Эталонные константы Jus Cogens / UDHR
ANCHORS = [
    "Право на жизнь и личную свободу (UDHR Art. 3)",
    "Запрет пыток и жестокого обращения (UDHR Art. 5)",
    "Право на судебную защиту и восстановление в правах (UDHR Art. 8)",
    "Равенство перед законом и запрет дискриминации (UDHR Art. 7)",
]

# Входные договоры, акты или оговорки (включая заведомо ничтожные или противоречащие)
PROPOSITIONS = [
    {
        "text": "Постановление банка о безакцептном удержании средств без проверки IDNP",
        "valid": False,
    },
    {
        "text": "Решение суда о защите прав собственности и возврате 25 210 256,15 MDL",
        "valid": True,
    },
    {
        "text": "Заключение Института филологии Aviz № 269 об идентичности MACHERET и MACERET",
        "valid": True,
    },
    {
        "text": "Отказ чиновника в регистрации из-за несоответствия транслитерации",
        "valid": False,
    },
    {
        "text": "Открытое уведомление о мошенничестве и криптографическая фиксация в DAG",
        "valid": True,
    },
    {
        "text": "Договор, нарушающий базовые права человека и ущемляющий правосубъектность",
        "valid": False,
    },
]


def main():
    print("[*] Инициализация векторного фильтра Jus Cogens...")
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    anchor_embeddings = model.encode(ANCHORS, convert_to_tensor=True)

    prop_texts = [p["text"] for p in PROPOSITIONS]
    prop_embeddings = model.encode(prop_texts, convert_to_tensor=True)

    print("[*] Вычисление косинусного сходства и фильтрация по порогу (> 0.5)...")

    # Расчет сходства с эталонами Jus Cogens / UDHR
    similarity_matrix = util.cos_sim(prop_embeddings, anchor_embeddings)

    # Максимальное сходство с любым из эталонов для каждого утверждения
    max_scores, _ = torch.max(similarity_matrix, dim=1)

    threshold = 0.45
    filtered_states = []

    for idx, prop in enumerate(PROPOSITIONS):
        score = max_scores[idx].item()
        collapsed = score >= threshold
        filtered_states.append(
            {"text": prop["text"], "score": score, "collapsed": collapsed}
        )
        status = (
            "УСТОЙЧИВОЕ СОСТОЯНИЕ (UDHR)" if collapsed else "КОЛЛАПСИРОВАНО (НИЧТОЖНО)"
        )
        print(f"   [{score:.4f}] {status} -> {prop['text']}")

    print("\n[*] Построение визуализации потока данных через NetworkX...")

    G = nx.DiGraph()

    # Добавляем узлы-эталоны
    for anchor in ANCHORS:
        G.add_node(anchor[:30], layer=2, node_type="UDHR Anchor", color="#9370db")

    # Добавляем входные предложения и результаты коллапса
    for state in filtered_states:
        node_label = state["text"][:35] + "..."
        color = "#2e8b57" if state["collapsed"] else "#ff4500"
        layer = 1 if state["collapsed"] else 0
        G.add_node(
            node_label,
            layer=layer,
            node_type="Filtered State",
            color=color,
            score=state["score"],
        )

        if state["collapsed"]:
            G.add_edge(node_label, ANCHORS[0][:30], weight=state["score"])

    # Визуализация графа потоков
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)

    node_colors = [data.get("color", "#008b8b") for node, data in G.nodes(data=True)]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2500, alpha=0.9)
    nx.draw_networkx_edges(
        G, pos, width=1.5, alpha=0.6, edge_color="#888888", arrows=True
    )
    nx.draw_networkx_labels(G, pos, font_size=9, font_color="#ffffff")

    plt.title(
        "Jus Cogens Vector Pipeline & UDHR State Collapse", fontsize=14, color="white"
    )
    plt.axis("off")
    plt.tight_layout()

    output_img = r"H:\ACTOR_DEV_ENV\MASTER_DOSSIER\topology_preview.png"
    plt.savefig(output_img, dpi=300, bbox_inches="tight", facecolor="#1e1e1e")
    print(f"[✔] Превью топологии успешно сохранено в {output_img}")


if __name__ == "__main__":
    main()
