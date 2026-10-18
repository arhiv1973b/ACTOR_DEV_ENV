import os
import hashlib

dossier_dir = r"H:\ACTOR_DEV_ENV\MASTER_DOSSIER"
files = [
    "00_Cover_Letter.md",
    "01_Topology_TI-ULA.md",
    "02_Legal_Memorandum.md",
    "03_DigitalTrace_Block.md",
    "05_Cryptographic_Anchors.md",
    "06_Timeline_Restitutio.md",
]

hashes = {}
for f in files:
    path = os.path.join(dossier_dir, f)
    if os.path.exists(path):
        with open(path, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
            hashes[f] = h

cover_letter_path = os.path.join(dossier_dir, "00_Cover_Letter.md")
content = f"""# COVER LETTER — MASTER DOSSIER SUBMISSION

**Case Reference:** CASE-MACHERET-1997-2026  
**Subject:** Submission of consolidated Master Dossier under UDHR 1948 framework  
**Date:** October 7, 2026  

---

## Addressed To:
- National Bank of Moldova  
- Ministry of Finance of Moldova  
- INI (Inspectoratul Național de Investigații)  
- The White House, Washington D.C.  
- Embassy of the United States in Chișinău  

---

## Purpose
This cover letter accompanies the **Master Dossier** package, compiled and cryptographically anchored for international compliance. The dossier consolidates forensic evidence, legal memoranda, and verified institutional records, ensuring integrity under SHA‑256 hashing and GPG‑signed commits.

---

## Content Overview
- **Topology & Legal Memorandum** — institutional mapping and legal framework.  
- **Digital Trace Block** — forensic automation logs and custody chain.  
- **Bloom Exports** — graph visualizations (PNG/SVG).  
- **Cryptographic Anchors** — immutable GitHub release references.  
- **Timeline Restitutio** — chronological reconstruction of events.  

---

## Cryptographic Hashes (SHA-256) of Dossier Components
"""

for f, h in hashes.items():
    if f != "00_Cover_Letter.md":
        content += f"- **{f}**: `{h}`\n"

content += """
---

## Compliance Basis
The submission is anchored in **Universal Declaration of Human Rights (UDHR, 1948)**, replacing all references to ECHR.  
Normative principles: *Erga Omnes* and *Jus Cogens*.

---

## Access
Full dossier and cryptographic anchors are available via secured GitHub repository release:  
`https://github.com/arhiv1973b/ACTOR_DEV_ENV/releases`

---

## Declaration
All attached materials are verified, hashed, and immutable.  
This submission is intended for regulatory, judicial, and diplomatic review.

---

**Submitted by:**  
Alexei Macheret (A©tor)  
Chișinău, Moldova  
GPG Fingerprint / MoldSign Signature: Verified
"""

with open(cover_letter_path, "w", encoding="utf-8") as fh:
    fh.write(content)

print("Cover letter updated successfully with SHA-256 hashes.")
