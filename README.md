# Invariant Evidence System: Case Maceret 1997-2026

## Declaration of Truth
Эта система создана как вычислительный барьер против процедурного обнуления фактов.
Верховенство факта обеспечено неизменяемым реестром (Append-only) и математическим инвариантом L0.

## Architecture
- L0: Immutable Invariant (Jus Cogens)
- L1: Evidence DAG
- L2: Temporal Graph
- L2.5: LTL Auditor (Fact Supremacy)

## Finalization & Evidence Integrity
The repository includes the automated audit and sanitization script `finalize_repo.sh`, which enforces cryptographic rigor and repository hygiene:
- **Canonical Identity:** Automatically enforces verification under the verified canonical address (`arhiv240@gmail.com`) across git metadata and commit signatures.
- **Evidence Integrity:** Cleans up submodule nesting issues (`gemini-skills`), stages forensic reports, and securely synchronizes immutable nodes to GitHub while isolating heavy cold storage archives (`MASTER_DOSSIER/Cold_Storage/`) via `.gitignore`.
