import json
import os
import glob

print("Чтение локальных файлов и реестров для построения графа доказательств...")

vis_nodes = []
vis_edges = []

# Добавляем ключевые якорные узлы текущей сессии
anchors = [
    {
        "id": "ets-nr-2-anchor",
        "label": "[ets-nr-2-anchor]\nHistorical Defect of ECHR - ETS nr. 2",
        "color": "#c8960a",  # Gold
        "desc": "ETS nr. 2 (02.09.1949) vs Jus Cogens / UDHR 1948",
    },
    {
        "id": "un-petition-s22-anchor",
        "label": "[un-petition-s22-anchor]\nUN Petition & S-22 Anchor",
        "color": "#9933cc",  # Purple
        "desc": "S-22 (1998) torture finding and UN 2022 Petition",
    },
]

for a in anchors:
    vis_nodes.append(
        f"{{id: '{a['id']}', label: \"{a['label']}\", color: '{a['color']}', shape: 'box'}}"
    )

# Связываем якоря с ключевыми концептами
vis_edges.append(
    "{from: 'ets-nr-2-anchor', to: 'un-petition-s22-anchor', label: 'activates jus cogens'}"
)

# Читаем remote_drive_manifest.json если есть
remote_manifest_path = "MASTER_DOSSIER/remote_drive_manifest.json"
if os.path.exists(remote_manifest_path):
    try:
        with open(remote_manifest_path, "r", encoding="utf-8-sig") as f:
            remote_entries = json.load(f)
        for idx, entry in enumerate(remote_entries[:50]):  # limit to 50 for clarity
            fname = entry.get("FileName", "unknown")
            sha = entry.get("Sha256", "UNKNOWN")
            sha_short = sha[:8] if len(sha) >= 8 else sha
            node_id = f"remote_drive_{idx}"
            color = "#008b8b"  # Teal for remote metadata-only files
            if entry.get("IdnpMatch") or entry.get("MatchedVariants"):
                color = "#ff1493"  # Deep pink for IDNP/Surname variant match

            label = f"[REMOTE:{sha_short}]\n{fname[:30]}..."
            vis_nodes.append(
                f"{{id: '{node_id}', label: \"{label}\", color: '{color}', shape: 'box'}}"
            )
            vis_edges.append(
                f"{{from: 'un-petition-s22-anchor', to: '{node_id}', label: 'remote metadata ref'}}"
            )
    except Exception as e:
        print(f"Error loading remote drive manifest for graph: {e}")
for i in range(1, 8):
    chunk_path = f"registry_chunks/registry_chunk_{i}.json"
    if os.path.exists(chunk_path):
        try:
            with open(chunk_path, "r", encoding="utf-8") as f:
                chunk = json.load(f)
            for node in chunk.get("evidence_nodes", []):
                node_id = node.get("node_id")
                doc_ref = node.get("document_ref", "").lower()

                color = "#4a4a4a"
                if "1-568" in doc_ref:
                    color = "#cc0000"
                elif "fincombank" in doc_ref or "nbm" in doc_ref:
                    color = "#ff8c00"
                elif (
                    "jus_cogens" in doc_ref
                    or "venice" in doc_ref
                    or "ets" in doc_ref
                    or "s-22" in doc_ref
                ):
                    color = "#0000cc"

                if color != "#4a4a4a":
                    label = (
                        f"[{node_id}]\n{node.get('document_ref', 'Unknown')[:30]}..."
                    )
                    vis_nodes.append(
                        f"{{id: '{node_id}', label: \"{label}\", color: '{color}', shape: 'box'}}"
                    )
        except Exception:
            pass

# Читаем edges.json если есть
edges_path = "registry_chunks/edges.json"
node_ids = [n.split("id: '")[1].split("'")[0] for n in vis_nodes]
if os.path.exists(edges_path):
    try:
        with open(edges_path, "r", encoding="utf-8") as f:
            edges_data = json.load(f)
        for edge in edges_data.get("edges", []):
            if edge["source"] in node_ids or edge["target"] in node_ids:
                vis_edges.append(
                    f"{{from: '{edge['source']}', to: '{edge['target']}', label: '{edge.get('relation', '')}'}}"
                )
    except Exception:
        pass

html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TI-ULA Evidence Graph: CASE-MACHERET-1997-2026 (Updated)</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style type="text/css">
    body {{ background-color: #050a0f; color: #c0d8ec; font-family: 'Rajdhani', sans-serif; margin: 0; }}
    #mynetwork {{ width: 100vw; height: 100vh; border: none; }}
    #legend {{ position: absolute; top: 10px; left: 10px; background: rgba(6,15,26,0.9); border: 1px solid #0c2e4a; padding: 15px; border-radius: 4px; z-index: 10; font-family: 'Share Tech Mono', monospace; font-size: 13px; }}
  </style>
</head>
<body>
<div id="legend">
    <h3 style="color:#f0c040; margin-bottom: 10px;">CASE-MACHERET 1997–2026</h3>
    <p><span style="color:#cc0000;">■</span> Detention (Root Cause: 1-568/98)</p>
    <p><span style="color:#ff8c00;">■</span> Financial Blockade (Fincombank)</p>
    <p><span style="color:#0000cc;">■</span> Jus Cogens / Venice / ETS</p>
    <p><span style="color:#008b8b;">■</span> Remote Drive Metadata (No Copy)</p>
    <p><span style="color:#ff1493;">■</span> IDNP / Surname Variant Match</p>
</div>
<div id="mynetwork"></div>
<script type="text/javascript">
  var nodes = new vis.DataSet([{",".join(vis_nodes)}]);
  var edges = new vis.DataSet([{",".join(vis_edges)}]);
  var container = document.getElementById('mynetwork');
  var data = {{ nodes: nodes, edges: edges }};
  var options = {{ edges: {{ arrows: 'to', color: '#8ab0cc' }}, physics: {{ stabilization: false, barnesHut: {{ springLength: 200 }} }} }};
  var network = new vis.Network(container, data, options);
</script>
</body>
</html>
"""

with open("evidence_map.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Успех! Обновленный граф сохранен в файл: evidence_map.html")
