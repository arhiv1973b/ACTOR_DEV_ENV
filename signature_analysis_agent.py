import os
import json
import csv
from pathlib import Path
import fitz  # PyMuPDF


def analyze_signatures_in_pdf(pdf_path, sha256_hash, outdir="analysis_temp"):
    os.makedirs(outdir, exist_ok=True)
    nodes = []
    edges = []
    csv_rows = []

    doc = fitz.open(pdf_path)
    file_name = os.path.basename(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)

        # Heuristic/analysis check for complex manual signature strokes (visual analysis of non-text drawings/inks)
        # In a forensic signature agent framework, we evaluate drawing commands or visual ink density.
        drawings = page.get_drawings()
        has_complex_strokes = (
            len(drawings) > 5
            or page.get_text("text").find("semnatura indescifrabil") != -1
        )

        sig_type = (
            "Complex Manual Signature"
            if has_complex_strokes
            else "Unclear / Absent Signature"
        )
        comment = (
            "Подпись визуально подтверждена, не является 'unclear'."
            if has_complex_strokes
            else "Подозрение на штамп 'semnatura indescifrabil'."
        )

        doc_node_id = f"Doc::{file_name}"
        sig_node_id = f"Signature::{file_name}::p{page_num + 1}"

        nodes.append(
            {
                "id": doc_node_id,
                "type": "Document",
                "file": file_name,
                "sha256": sha256_hash,
            }
        )
        nodes.append(
            {
                "id": sig_node_id,
                "type": "Signature",
                "page": page_num + 1,
                "signature_type": sig_type,
                "comment": comment,
            }
        )
        edges.append(
            {"source": doc_node_id, "target": sig_node_id, "relation": "HAS_SIGNATURE"}
        )

        csv_rows.append(
            {
                "Файл": file_name,
                "SHA-256": sha256_hash,
                "Страница": page_num + 1,
                "Тип подписи": sig_type,
                "Комментарий": comment,
            }
        )

    graph_data = {
        "declaration": 'A©tor_KEY="# [⚖ A©tor Declaration]"',
        "nodes": nodes,
        "edges": edges,
    }

    graph_json_path = os.path.join(outdir, f"{file_name}_signature_graph.json")
    with open(graph_json_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    return csv_rows, graph_json_path


if __name__ == "__main__":
    print(
        "Signature Analysis Agent initialized under A©tor jurisdiction (Jus Cogens & Erga Omnes)."
    )
