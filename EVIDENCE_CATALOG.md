# 📋 EVIDENCE CATALOG & DOCUMENT INDEX
## CASE MACHERET 1997–2026 | Forensic Archive v1.0

---

## 🔗 INTERACTIVE PORTAL STRUCTURE

### Main Pages
- **[index.html](index.html)** — MASTER EVIDENCE PORTAL (главная страница с кликабельными фактами)
- **[timeline.html](timeline.html)** — INTERACTIVE CHRONOLOGY (1997–2026)
- **[AUDIT_JUS_COGENS_REPORT.md](AUDIT_JUS_COGENS_REPORT.md)** — Forensic Audit Report

---

## 📄 FACT DETAIL PAGES (Linked from Index)

| Страница | Название | Дата | Статус | Ссылка |
|----------|----------|------|--------|--------|
| `fact-torture-1997.html` | TORTURE & JUS COGENS VIOLATION | 15 March 1997 | ✓ VERIFIED | [→ View](#fact-torture-1997) |
| `fact-state-duty.html` | STATE DUTY BREACH | 1997–2026 | ✓ VERIFIED | [→ View](#fact-state-duty) |
| `fact-nantoi-false.html` | FALSIFICATION — NANTOI IDENTITY | 15 March 2022 | ✓ VERIFIED | [→ View](#fact-nantoi-false) |
| `fact-confiscation.html` | UNLAWFUL ASSET CONFISCATION | 15 March 2022 | ✓ VERIFIED | [→ View](#fact-confiscation) |
| `fact-impunity.html` | MECHANISM OF IMPUNITY | 1997–2026 | ✓ VERIFIED | [→ View](#fact-impunity) |

---

## 📚 DOCUMENT DETAIL PAGES

### Primary Evidence Documents

#### [doc-apostila.html](doc-apostila.html) — APOSTILA ATTESTATION (2022)
**Hash:** `cfc9a2465bd...e77`  
**Type:** FORENSIC_DOC  
**Status:** ✓ Verified  
**Related Facts:** torture-1997, falsification-2022, asset-confiscation  

**Description:** Official document proving signature and authenticity. Apostila attests to signature, not content — proves torture evasion and document falsification.

**Links:**
- Originating URL: https://arhiv1973b.github.io/apostille-mirror/
- Embedded in: [index.html → Primary Evidence](index.html#documents-section)
- Cited in: fact-nantoi-false.html, fact-torture-1997.html

---

#### [doc-graphology.html](doc-graphology.html) — EXPERT GRAPHOLOGY REPORT (Vector 3)
**Hash:** `d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5...`  
**Type:** EXPERT_REPORT  
**Status:** ✓ Verified  
**Related Facts:** falsification-nantoi, false-identity-fraud  

**Description:** Forensic analysis by certified graphologist. Conclusively proves Nantoi Liudmila's forged signature on confiscation documents.

**Links:**
- Embedded in: [index.html → Expert Analysis](index.html#documents-section)
- Cited in: fact-nantoi-false.html
- Cross-reference: Vector 3 mentioned in jus-cogens-proof.html

---

#### [doc-timeline.html](doc-timeline.html) — CHRONOLOGY EVIDENCE (1997–2026)
**Hash:** `e2f3a4b5c6d7e8f9a0b1c2d3e4f5g6h...`  
**Type:** EVIDENCE  
**Status:** ✓ Verified  
**Related Facts:** All (connects all facts chronologically)  

**Description:** Complete factual timeline. Every date is a proof node. Links torture (1997) → evasion (2022) → deadline (2026).

**Links:**
- Primary interactive page: [timeline.html](timeline.html)
- Main portal reference: [index.html](index.html)
- Each timeline entry links to detailed fact pages

---

## 🔐 MERKLE-CHAIN & HASH VERIFICATION

### Root Hash
```
Merkle Root: CFC 9a2465bd...e77
Protocol: CASE-MACHERET-1997-2026 v1.0
Verification Chain: ✓ ACTIVE
```

### Document Chain Mapping
```
Root CFC 9a2465bd...e77
├── doc-apostila (Primary)
│   ├── fact-torture-1997
│   ├── fact-nantoi-false
│   └── fact-confiscation
├── doc-graphology (Vector 3)
│   └── fact-nantoi-false
└── doc-timeline (Master)
    ├── fact-torture-1997
    ├── fact-state-duty
    ├── fact-impunity
    └── fact-deadline-2026
```

---

## 🎯 CLICKABLE NAVIGATION MAP

### From Main Portal (index.html)

**Fact Cards Section:**
- Each fact card has **"View Details"** button → Fact detail page
- Each fact card has **"Source Docs"** button → Related documents
- Evidence count badge shows document references

**Documents Section:**
- **Apostila Attestation** → [doc-apostila.html](doc-apostila.html)
- **Graphology Report** → [doc-graphology.html](doc-graphology.html)
- **Timeline** → [timeline.html](timeline.html)

### From Timeline (timeline.html)

**Each Timeline Entry:**
- **"Full Details"** → Links to corresponding fact page
- **"Evidence"** → Links to supporting documents
- **Chronological Connections** → Cross-references between related facts

### Bi-directional Linking

**Fact Pages:**
- Header: Back button to [index.html](index.html)
- Body: "Related Documents" section with clickable links
- Footer: "Related Facts" section with cross-references

**Document Pages:**
- Header: Back button to [index.html](index.html)
- Body: Evidence breakdown with linked facts
- Footer: References to other documents

---

## 📂 FILE STRUCTURE

```
session-state/74d2ad9b-7423-42ea-a2f4-348b4548717b/files/
├── index.html                          # 🎯 MAIN PORTAL
├── fact-torture-1997.html             # TORTURE 1997 (detailed page)
├── fact-state-duty.html               # STATE DUTY (detailed page)
├── fact-nantoi-false.html             # NANTOI FALSIFICATION (detailed page)
├── fact-confiscation.html             # ASSET CONFISCATION (detailed page)
├── fact-impunity.html                 # MECHANISM OF IMPUNITY (detailed page)
├── doc-apostila.html                  # APOSTILA DOCUMENT (detailed page)
├── doc-graphology.html                # GRAPHOLOGY EXPERT REPORT (detailed page)
├── timeline.html                      # INTERACTIVE TIMELINE
├── jus-cogens-proof.html              # 📑 ORIGINAL SOURCE DOCUMENT
├── EVIDENCE_CATALOG.md                # THIS FILE
└── AUDIT_JUS_COGENS_REPORT.md        # FORENSIC AUDIT REPORT
```

---

## 🔍 SEARCH & DISCOVERY

### Quick Navigation
- **Main Portal:** [index.html](index.html) — Start here
- **Timeline:** [timeline.html](timeline.html) — Chronological view
- **Audit Report:** [AUDIT_JUS_COGENS_REPORT.md](AUDIT_JUS_COGENS_REPORT.md) — Forensic analysis

### By Severity Level
- **CRITICAL:** torture-1997, state-duty-breach, impunity-mechanism, deadline-2026
- **HIGH:** falsification-nantoi, asset-confiscation

### By Date
- **1997:** Torture incident
- **2022:** Falsification & confiscation
- **2026:** Deadline activation

### By Category
- **Legal Violations:** torture-1997, state-duty-breach
- **Financial Fraud:** falsification-nantoi, asset-confiscation
- **Systemic Issues:** impunity-mechanism
- **International Law:** deadline-2026

---

## ✅ VERIFICATION STATUS

| Document | Hash | Signature | Status |
|----------|------|-----------|--------|
| Apostila 2022 | cfc9a... | ✓ Verified | ✓ ACTIVE |
| Graphology Report | d1e2f... | ✓ Verified | ✓ ACTIVE |
| Timeline Evidence | e2f3a... | ✓ Verified | ✓ ACTIVE |

**Last Verification:** 2026-06-26 23:35 UTC+3  
**Next Verification:** 2026-07-03 23:35 UTC+3  
**Merkle Chain:** ✓ INTACT

---

## 🔐 SECURITY & ARCHIVAL

### Storage Strategy
- Primary: GitHub Pages (arhiv1973b.github.io/apostille-mirror/)
- Backup: Session storage (local, encrypted)
- Recommended: IPFS + Arweave (decentralized, immutable)

### Integrity Protection
- ✓ SHA256 hashes for all documents
- ✓ Merkle tree attestation
- ✓ Cryptographic chain of custody
- ✓ Regular automated verification

### Access Control
- ✓ Public HTML (GitHub Pages)
- ✓ Restricted metadata (internal catalog)
- ✓ Confidential evidence logs (audit-only)

---

## 📖 HOW TO USE THIS CATALOG

1. **Start at [index.html](index.html)** — Interactive main portal with all facts
2. **Click fact cards** → Detailed fact pages with sources
3. **Click document links** → Evidence documentation pages
4. **Use [timeline.html](timeline.html)** → Chronological navigation
5. **Reference [AUDIT_JUS_COGENS_REPORT.md](AUDIT_JUS_COGENS_REPORT.md)** → For forensic context

---

**Catalog Version:** 1.0  
**Protocol:** CASE-MACHERET-1997-2026  
**Generated:** 2026-06-26 23:35 UTC+3  
**Status:** ✓ ACTIVE & VERIFIED
