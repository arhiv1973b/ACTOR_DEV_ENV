---
document_id: "PRIMARY-EVIDENCE-INTAKE-TEMPLATE-20261020"
case: "CASE-MACHERET-1997-2026"
related_summary: "FT-SUMMARY-20261020-L0"
status: "TEMPLATE"
date: "2026-10-20"
a©tor_key: "# [⚖ A©tor Declaration]"
---

# Primary Evidence Intake Template

**Purpose:** Standardized intake form for primary source documents required to upgrade financial and infrastructure claims from USER_ASSERTED to VERIFIED.

**Target directory:** `evidence/financial_sabotage/`

---

## Intake Table

| Field | Primary Evidence – FinComBank | Primary Evidence – GitHub Billing |
|-------|-------------------------------|-----------------------------------|
| **Filename (proposed)** | `FINCOMBANK_EMBARGO_NOTICE_2026.pdf` (or series) | `GITHUB_INVOICE_JUNE_AUG_2026.pdf` / `.eml` / series |
| **Source** | Official statement / response / extract from FinComBank S.A. | Email from billing@github.com or GitHub Billing Portal export |
| **Key attributes to verify** | IDNP `2000001159655`; amount `25,210,256.15 MDL`; dates of restriction / freeze; legal basis stated by bank | Account `arhiv1973b`; rejection / failure logs covering 23.06–16.08.2026; invoice numbers; payment method |
| **Acquisition method** | Direct download / official channel / certified copy | Email archive / Billing Portal PDF / API export |
| **Acquisition timestamp** | (to be filled) | (to be filled) |
| **SHA-256 (computed before import)** | (to be filled) | (to be filled) |
| **Repository path after intake** | `evidence/financial_sabotage/` | `evidence/financial_sabotage/` |
| **Linked to** | `FINCOMBANK_GITHUB_BILLING_ANCHOR.md` | `FINCOMBANK_GITHUB_BILLING_ANCHOR.md` |
| **Verification status after intake** | VERIFIED / PARTIAL / NOT_VERIFIED | VERIFIED / PARTIAL / NOT_VERIFIED |
| **Notes / chain of custody** | | |

---

## Intake Checklist (per file)

- [ ] Original filename and source recorded
- [ ] Acquisition timestamp and method recorded
- [ ] SHA-256 computed on the **actual file bytes** before any modification
- [ ] File placed in `evidence/financial_sabotage/` without alteration
- [ ] Entry added to evidence DAG / relevant manifest
- [ ] Cross-reference to `FINCOMBANK_GITHUB_BILLING_ANCHOR.md` established
- [ ] Status updated in FORENSIC_TIMELINE_SUMMARY

---

## Notes on Status Transition

- A file becomes **VERIFIED** for integrity purposes once its SHA-256 is recorded and the file is under version control.
- The **content claims** (amounts, dates, causal statements) remain subject to independent evaluation even after the file itself is integrity-verified.
- Causation between the banking event and GitHub billing degradation stays **NOT_VERIFIED** until both primary sets of records are present and a chronological/causal analysis is completed.
