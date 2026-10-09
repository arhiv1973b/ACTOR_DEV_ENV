import os
import json

JSON_REPORT = r"H:\ACTOR_DEV_ENV\VECTOR_ENTITY_EXTRACTION_REPORT.json"
HTML_OUTPUT = r"H:\ACTOR_DEV_ENV\entity_graph_network.html"


def main():
    if not os.path.exists(JSON_REPORT):
        print(f"JSON report not found: {JSON_REPORT}")
        return

    with open(JSON_REPORT, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("extracted_records", [])

    nodes_list = []
    edges_list = []

    # Добавим центральные якорные узлы
    nodes_list.append(
        "{id: 'anchor_idnp', label: 'IDNP: 2000001159655\\n(Личность / Субъект)', color: '#ff4500', shape: 'ellipse'}"
    )
    nodes_list.append(
        "{id: 'anchor_assets', label: 'Активы: 25,210,256.15 MDL\\n(Финансовая константа)', color: '#ffd700', shape: 'ellipse'}"
    )
    nodes_list.append(
        "{id: 'anchor_aviz', label: 'Aviz № 269\\n(Институт филологии)', color: '#9370db', shape: 'ellipse'}"
    )

    edges_list.append(
        "{from: 'anchor_idnp', to: 'anchor_assets', label: 'связанные активы'}"
    )
    edges_list.append(
        "{from: 'anchor_idnp', to: 'anchor_aviz', label: 'лингвистическая верификация'}"
    )

    node_ids = set(["anchor_idnp", "anchor_assets", "anchor_aviz"])

    # Обрабатываем записи и добавляем узлы сущностей
    for idx, rec in enumerate(records[:100]):
        fname = rec.get("filename", f"file_{idx}")
        ent = rec.get("extracted_entities", {})

        file_node_id = f"file_{idx}"
        safe_fname = fname.replace("'", "\\'")
        nodes_list.append(
            f"{{id: '{file_node_id}', label: '{safe_fname[:35]}', color: '#008b8b', shape: 'box'}}"
        )

        idnp_list = ent.get("idnp", [])
        amounts_list = ent.get("amounts", [])
        aviz_list = ent.get("aviz", [])
        courts_list = ent.get("courts", [])

        if idnp_list:
            edges_list.append(
                f"{{from: '{file_node_id}', to: 'anchor_idnp', label: 'содержит IDNP'}}"
            )
        if amounts_list:
            edges_list.append(
                f"{{from: '{file_node_id}', to: 'anchor_assets', label: 'сумма MDL'}}"
            )
        if aviz_list:
            edges_list.append(
                f"{{from: '{file_node_id}', to: 'anchor_aviz', label: 'ссылка Aviz'}}"
            )

        for court in courts_list:
            safe_court = court.replace("'", "\\'")
            court_id = f"court_{abs(hash(court)) % 10000}"
            if court_id not in node_ids:
                nodes_list.append(
                    f"{{id: '{court_id}', label: 'Суд: {safe_court}', color: '#2e8b57', shape: 'diamond'}}"
                )
                node_ids.add(court_id)
            edges_list.append(
                f"{{from: '{file_node_id}', to: '{court_id}', label: 'юрисдикция'}}"
            )

    nodes_js = ", ".join(nodes_list)
    edges_js = ", ".join(edges_list)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Forensic Entity Graph Network</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #1e1e1e; color: #fff; margin: 0; padding: 20px; }}
        h1 {{ color: #00d2ff; }}
        #network {{ width: 100%; height: 800px; border: 1px solid #444; background-color: #252525; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>Forensic Entity Graph & Vector Network (IDNP ↔ Aviz ↔ Court ↔ Amount)</h1>
    <p>Интерактивный граф связей юридических сущностей, извлеченных из DAG-матрицы и векторных индексов.</p>
    <div id="network"></div>

    <script type="text/javascript">
        var nodes = new vis.DataSet([{nodes_js}]);
        var edges = new vis.DataSet([{edges_js}]);

        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{ font: {{ color: '#ffffff', size: 14 }} }},
            edges: {{ font: {{ color: '#aaaaaa', size: 10, align: 'middle' }}, color: {{ color: '#888888' }}, arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }} }},
            physics: {{ barnesHut: {{ gravitationalConstant: -30000, centralGravity: 0.4, springLength: 95, springConstant: 0.04 }} }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Interactive entity graph HTML generated successfully at {HTML_OUTPUT}")


if __name__ == "__main__":
    main()
