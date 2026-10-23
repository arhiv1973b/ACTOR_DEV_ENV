import os
import yaml
import json
from datetime import datetime

EVIDENCE_DIR = "evidence"
OUTPUT_FILE = "CASE_MACHERET_1997_2026_DOSSIER.md"

VALID_NODE_IDS = {
    "NODE_LEGAL_BASIS_JUS_COGENS",
    "NODE_REABILITARE_MACHERET_OLEINIK_NEGRU_2026",
    "SUBNODE_PROPERTY_RESTITUTION_1977_2026",
    "NODE_TORTURE_AND_COVERUP_1997_1998",
    "NODE_CONTINUING_CONSEQUENCES_1997_2026",
    "NODE_FINANCIAL_MODEL_1997_2026",
    "FINANCIAL_MODEL_DAMNUM_EMERGENS_LUCRUM_CESSANS_2026",
    "TI_ULA_MASTER_DAG_REGISTRY_2026",
    "LINK_NON_REHABILITATION_JUS_COGENS",
    "LINK_ACCOUNTABILITY_TO_CONSEQUENCES",
    "NODE_ENTITY_ACCOUNTABILITY_NETWORK",
    "ORDER_RISCANI_24JUL2007",
    "NODE_CSJ_DECISION_2009",
    "NODE_APOSTILLE_REGISTRY_MASTER",
    "NODE_SEMNATURA_INDESCIFRABILA_TRAP",
    "NODE_FICTITIOUS_ISSUANCE_TRAP",
    "NODE_ECHR_OVERRIDE_VCLT_UNRES4034",
    "NODE_GEOPOLITICAL_JUS_COGENS_SABOTAGE",
    "NODE_GERMANY_HAGUE_SABOTAGE",
    "NODE_VENICE_COMMISSION_TERROR_AND_IMMUNITY",
    "NODE_ECONOMIC_MAUROUDING_GRIGORAS",
    "NODE_TI_ULA_GRAPHVIZ_ARCHITECTURE",
    "DIVORCE_CERTIFICATE_MATIUK_STANISLAV_GALINA",
    "MARRIAGE_CERTIFICATE_GALINA_MACHERET",
    "ADOPTION_REASONING_1977",
    "NODE_TI_ULA_MASTER_TOPOLOGY",
    "CASCADE_CANCELLATION_MATRIX",
    "NODE_COMPREHENSIVE_EVIDENCE_BLOCK_2026",
    "NODE_COMPREHENSIVE_FINANCIAL_AND_FAMILY_TERROR_2026",
    "NODE_FINANCIAL_AND_DIGITAL_CONSOLIDATION_v2",
    "NODE_APOSTILLE_REGISTRY_FIXED_HTML",
    "NODE_AVIZ_INSTiintare_2023",
    "NODE_OPERATIONAL_DEPLOYMENT_v15",
}


def load_nodes():
    nodes = []
    if not os.path.exists(EVIDENCE_DIR):
        return nodes
    for filename in os.listdir(EVIDENCE_DIR):
        filepath = os.path.join(EVIDENCE_DIR, filename)
        data = None
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except Exception as e:
                pass
        elif filename.endswith(".json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                pass

        if isinstance(data, dict):
            node_id = data.get("id")
            if (
                node_id in VALID_NODE_IDS
                or filename.startswith("NODE_")
                or filename.startswith("LINK_")
                or filename.startswith("SUBNODE_")
                or filename.startswith("FINANCIAL_")
                or filename.startswith("TI_ULA_")
                or filename.startswith("CASCADE_")
            ):
                if data not in nodes:
                    nodes.append(data)
    return nodes


def generate_markdown_dossier(nodes):
    dossier = [
        "# LEGAL DOSSIER: CASE-MACHERET-1997-2026",
        f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Europe/Chisinau)",
        "**Legal Framework:** Universal Declaration of Human Rights (UDHR), Jus Cogens, Erga Omnes",
        "**Verification Protocol:** TI-ULA (Cryptographic Hashing & Pointer Isolation)",
        "---\n",
    ]

    order = {
        "root_legal_trust_node": 1,
        "evidence_node": 2,
        "evidence_subnode": 3,
        "property_restitution_subnode": 3,
        "verification_link": 4,
        "entity_mapping_node": 5,
        "damage_calculation_node": 6,
        "economic_restitution_model": 6,
        "cancellation_matrix_node": 7,
        "causation_link": 8,
        "master_registry": 9,
    }

    sorted_nodes = sorted(nodes, key=lambda x: order.get(x.get("type", ""), 99))

    for node in sorted_nodes:
        dossier.append(f"## Node: {node.get('id', 'UNKNOWN_NODE')}")
        dossier.append(f"**Type:** {node.get('type', 'N/A')}")

        if "legal_framework" in node:
            dossier.append("### Legal Framework")
            dossier.append(
                "```yaml\n"
                + yaml.dump(node["legal_framework"], allow_unicode=True)
                + "```"
            )

        if "legal_foundations" in node:
            dossier.append("### Legal Foundations (Root of Trust)")
            dossier.append(
                "```yaml\n"
                + yaml.dump(node["legal_foundations"], allow_unicode=True)
                + "```"
            )

        if "master_files" in node:
            dossier.append("### Cryptographic Anchors (Master Files)")
            for mf in node["master_files"]:
                dossier.append(f"- **File:** `{mf.get('filename')}`")
                dossier.append(f"  - **SHA-256:** `{mf.get('sha256')}`")
                dossier.append(f"  - **Role:** {mf.get('role', 'N/A')}")

        if "entities" in node:
            dossier.append("### Entity Accountability Network")
            for ent in node["entities"]:
                dossier.append(
                    f"- **{ent.get('name')}** ({ent.get('role')}): {ent.get('action')}"
                )

        if "components" in node:
            dossier.append("### Financial & Moral Claim (Provisional)")
            dossier.append(
                "```yaml\n" + yaml.dump(node["components"], allow_unicode=True) + "```"
            )
            if (
                "ti_ula_status" in node
                and "total_base_claim_eur" in node["ti_ula_status"]
            ):
                dossier.append(
                    f"**Total Provisional Claim:** {node['ti_ula_status']['total_base_claim_eur']} EUR"
                )

        if "verification_points" in node:
            dossier.append("### Verification Points")
            for vp in node["verification_points"]:
                dossier.append(f"- **File:** `{vp.get('file_ref')}`")
                dossier.append(f"  - **Mapping:** {vp.get('legal_mapping')}")
                if "violation" in vp:
                    dossier.append(f"  - **Violation:** {vp.get('violation')}")
                dossier.append(f"  - **Status:** `{vp.get('status')}`")

        if "causation_vectors" in node:
            dossier.append("### Causation Vectors")
            for cv in node["causation_vectors"]:
                dossier.append(f"- **Entity Group:** {cv.get('entity_group')}")
                dossier.append(f"  - **Action:** {cv.get('action')}")
                dossier.append(f"  - **Effect:** {cv.get('effect')}")

        dossier.append("\n---\n")

    return "\n".join(dossier)


def main():
    if not os.path.exists(EVIDENCE_DIR):
        print(f"Error: Directory '{EVIDENCE_DIR}' not found.")
        return

    nodes = load_nodes()
    markdown_content = generate_markdown_dossier(nodes)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Success: Consolidated dossier generated at '{OUTPUT_FILE}'.")
    print(f"Total cryptographic nodes processed: {len(nodes)}")


if __name__ == "__main__":
    main()
