import json
import datetime

claim_manifest = {
    "schema_version": "1.0.0",
    "case_id": "CASE-MACHERET-1997-2026",
    "generated_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "legal_basis": {
        "framework": "Universal Declaration of Human Rights (UDHR)",
        "article": "17.2",
        "article_text": "No one shall be arbitrarily deprived of his property.",
        "qualification": "DIRECT_VIOLATION_EXPROPRIATION",
    },
    "financial_anchor": {
        "commit_hash": "90655f14",
        "amount": 25210256.15,
        "currency": "MDL",
        "status": "EXPROPRIATED_UNRESOLVED",
    },
    "chain_of_custody": {
        "verification_status": "100_PERCENT_INTEGRITY",
        "missing_files_count": 0,
        "dag_manifest_linked": True,
        "git_lfs_secured": True,
    },
    "public_distribution": {
        "mirror_repository": "apostille-mirror",
        "github_pages_deployment": True,
        "visual_artifacts": ["dag_udhr17.png", "dag_udhr17.dot"],
    },
}

output_path = "udhr_claim_manifest.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(claim_manifest, f, indent=4, ensure_ascii=False)

print(f"Successfully generated {output_path}")
