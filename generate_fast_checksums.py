import os
import hashlib
from pathlib import Path

def generate_fast_checksums(output_path="05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    target_files = [
        "Legal_Act_Apostille_Audit_1997_2026.md",
        "apostilles_registry_90.json",
        "apostilles_registry_90.yaml",
        "signature_audit_matrix.csv",
        "signature_audit_matrix_extended.csv",
        "signature_evidence_graph.dot",
        "03_GRAPH_GRAPHICS/signature_evidence_graph.svg",
        "AUDIT_MEMORANDUM_SIGNATURE_EXPERT.md",
        "README_DEPOSITARY_INDEX.md",
        "COVER_LETTER_INTERNATIONAL_SUBMISSION.md"
    ]
    
    lines = []
    for tf in target_files:
        path = Path(tf)
        if path.exists() and path.is_file():
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            sha = h.hexdigest()
            lines.append(f"{sha}  {tf}")
            
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        
    print(f"Fast checksums generated for {len(lines)} core files into {output_path}")

if __name__ == "__main__":
    generate_fast_checksums()
