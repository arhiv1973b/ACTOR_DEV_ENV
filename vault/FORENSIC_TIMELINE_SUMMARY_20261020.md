---
document_id: "FT-SUMMARY-20261020-L0"
case: "CASE-MACHERET-1997-2026"
sovereign_witness: "A©tor"
idnp: "2000001159655"
repo: "arhiv1973b/ACTOR_DEV_ENV"
pr_reference: "PR #2"
legal_scope: "UDHR 1948 (Art. 5, 8, 17, 25); Const. RM (Art. 4, 8); Jus Cogens / Erga Omnes"
status: "EVIDENCE_AUDIT_DRAFT"
date: "2026-10-20"
a©tor_key: "# [⚖ A©tor Declaration]"
---

# FORENSIC TIMELINE SUMMARY

**Case:** MACHERET / FINCOMBANK / GITHUB BILLING  
**Period:** June–August 2026  
**Primary Anchor:** `evidence/financial_sabotage/FINCOMBANK_GITHUB_BILLING_ANCHOR.md`  
**Repository:** `arhiv1973b/ACTOR_DEV_ENV` (PR #2)  
**Summary Date:** 2026-10-20  

---

### 1. Financial Event

| Item | Value | Status |
|------|-------|--------|
| Principal amount under dispute | 25,210,256.15 MDL | USER_ASSERTED (stated in anchor and multiple evidence JSON files) |
| Additional fee | 11.98 MDL | USER_ASSERTED (appears in secondary references) |
| Total stated amount | 25,210,268.13 MDL | USER_ASSERTED |
| Alleged restriction | Asset blockade / liquidity freeze by FinComBank S.A. linked to antroponymic discrepancy (`Maceret` vs `Macheret`) | USER_ASSERTED |
| IDNP referenced | 2000001159655 | USER_ASSERTED (consistent across anchor and identity files) |

**Required for upgrade to VERIFIED:**  
Original banking records, transaction identifiers, account statements, official correspondence from FinComBank, and independent confirmation of the restriction dates and legal basis.

---

### 2. Infrastructure Event

| Date (as stated in anchor) | Claimed Event | Status |
|----------------------------|---------------|--------|
| 23 June 2026 | Initial GitHub billing payment rejection for account `arhiv1973b` | USER_ASSERTED |
| 5 July 2026 | Secondary payment failure | USER_ASSERTED |
| 29 July 2026 | Third-tier billing blockage | USER_ASSERTED |
| 7–16 August 2026 | Cascade of rejections → forced subscription cancellation | USER_ASSERTED |

**Documented in repository (PR #2):**
- New file: `evidence/financial_sabotage/FINCOMBANK_GITHUB_BILLING_ANCHOR.md` (commit range including `1483850` / `4e51c2d`)
- Mass identity normalization (`A©TOR_KEY` → `A©tor_KEY`) across HTML, JSON, and Markdown files
- Updates to evidence DAG, manifests, and forensic JSON records

**Missing for independent verification:**  
GitHub billing invoices/receipts, email notifications from GitHub, workflow run logs, payment processor records, and exact timestamps of service degradation.

---

### 3. Evidence Integrity

| Artifact | Source | Acquisition | SHA-256 | Commit / Path | Verification Status |
|----------|--------|-------------|---------|---------------|---------------------|
| `FINCOMBANK_GITHUB_BILLING_ANCHOR.md` | Created in PR #2 | 2026-10-19 (repo timestamp) | Not yet computed on local bytes | `evidence/financial_sabotage/FINCOMBANK_GITHUB_BILLING_ANCHOR.md` | USER_ASSERTED (content of the anchor itself) |
| Related evidence JSON files (`evidence_*.json`, `transaction_c99741*`, etc.) | Updated in same PR | Repository commits | Present in manifests (to be re-verified) | Multiple paths under `evidence/` | PARTIALLY VERIFIED (file presence and commit history) / content claims remain USER_ASSERTED |
| Apostille and OCR derivatives | Bulk updates in PR | Various prior sources + reprocessing | Hashes listed in `pdf_manifest.json` and related manifests | `Apostilles/` directory | INTEGRITY of current bytes can be checked; authenticity of underlying documents requires original sources |

**Note:** A SHA-256 digest confirms that the bytes have not changed since hashing. It does not prove the truth of the statements contained in the document.

---

### 4. Legal Framework (Reference Only)

Provisions cited in the anchor and related materials:

- Universal Declaration of Human Rights (1948), Articles 5, 8, 17, 25  
- Constitution of the Republic of Moldova, Articles 4 and 8  
- References to *jus cogens* and *erga omnes* obligations  

These provisions are noted for analytical purposes. Their applicability and any alleged violation remain subject to assessment against independently verified facts and the specific legal elements of each norm.

---

### 5. Causation and Conclusion

**Current classification of the claimed causal link**  
(FinComBank asset restriction → synchronized GitHub billing degradation):  
**NOT_VERIFIED**

Reason: The chronological coincidence and identity-parity argument are asserted in the anchor document and supporting repository files. Independent primary records establishing both the banking restriction and the GitHub billing failures, together with a demonstrated causal mechanism, have not yet been produced or independently confirmed.

**Integrity objective (maintained):**  
- Preserve original evidence bytes  
- Make every transformation reproducible  
- Clearly separate:  
  – Documented repository facts (file existence, commit history, hashes)  
  – User-asserted content (financial amounts, dates, causal claims)  
  – Legal conclusions  

---

**Next recommended actions for strengthening the record:**
1. Obtain and hash original FinComBank statements / restriction notices.  
2. Obtain and hash GitHub billing notifications / invoices for June–August 2026.  
3. Compute and record SHA-256 of the current `FINCOMBANK_GITHUB_BILLING_ANCHOR.md` and key supporting files.  
4. Cross-reference transaction identifiers (if any) against bank and GitHub records.
