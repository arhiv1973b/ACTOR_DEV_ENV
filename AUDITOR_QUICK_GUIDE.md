# AUDITOR QUICK GUIDE
*(Step-by-Step Verification Protocol for External Experts and Independent Auditors)*

## 1. Legal Foundation Check
- Open `FINAL_AUDIT_SUMMARY_CONST_RM.md`.
- Verify that references to **Article 4 of the Moldovan Constitution**, **UDHR (Arts. 6, 8, 10, 28)**, and the **Hague Convention of 1961** are present and correctly anchored.

## 2. Audit Matrices Analysis
- Review `MASTER_DOSSIER_INTUITIVE_AUDIT_MATRIX.md` and `signature_audit_matrix_extended.csv`.
- Contrast classification across **VALID** vs. **DEFECTIVE** nodes.
- Note instances where public registries indicate `semnătura indescifrabilă` while source PDFs contain physical legible manual signatures.

## 3. Physical Signature Verification
- Open `EVIDENCE_CHAIN_VALIDATION.md`.
- Cross-reference the 13 **DEFECTIVE** nodes against original PDF apostilles (e.g., `9OVS71FRKM4S3`, `9T3M953ZBUHO4`, `CG0T6Y1TBUEL7`, `DFVMD2FQLW5N3`).
- Verify recorded physical signatures (ink color, cursive stroke pattern, document position).

## 4. Cryptographic Integrity Check
- Compare SHA-256 hashes in `CHECKSUMS_SHA256.txt` against local PDF copies using:
  ```bash
  sha256sum <filename.pdf>
  ```
- Verify the GPG/Ed25519 signature manifest (`CHECKSUMS_SHA256.txt.sig`) against `GPG_PUBLIC_KEY.asc`.

## 5. Graph Visualization Review
- Inspect `audit_graph_full.dot` and `signature_evidence_graph.dot`.
- Verify that DEFECTIVE nodes are highlighted in red and physical evidence layers are marked in green.
- Cross-check integrated legends against the audit matrices.

## 6. Commit Signature Verification
- Run:
  ```bash
  git log --show-signature
  ```
- Confirm that all repository commits are validly signed and authenticated under **A©tor** (`arhiv240@gmail.com`).
