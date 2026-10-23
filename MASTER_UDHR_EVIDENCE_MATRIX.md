# MASTER UDHR EVIDENCE MATRIX & LEGAL QUALIFICATION
**Case Reference:** MACHERET-1997-2026 / UDHR 1948 / VCLT Article 71 / Actus Nullus  
**Authentication Protocol:** A©tor Key / TI-ULA / SHA-256 / Ed25519 Cryptographic Anchoring  

---

## 📊 Evidence-to-Norm Correlation Table (Гос банк Молдовы.pdf & TI-ULA Pipeline)

| Fact / Evidence Item | Violated UDHR Article | Legal Qualification & Doctrinal Basis |
| :--- | :--- | :--- |
| **Blocking of 25,210,256.15 MDL** (FinComBank → Moldindconbank, Transaction `c99741`) | **Статья 17** (Right to property)<br>**Статья 9** (Arbitrary deprivation) | Arbitrary expropriation and withholding of private funds under color of institutional inaction; *continuing consequences*. |
| **Withholding of inheritance deposits** (G. I. Markova / 300 MDL fine pretext) | **Статья 17** (Right to property)<br>**Статья 6** (Legal personality) | Administrative harassment and procedural misuse of minor penalties to freeze rightful inheritance rights. |
| **Systemic prosecutorial inaction & refusal to investigate** (Gureev, Vacarciuc, Ciuperca) | **Статья 8** (Effective remedy)<br>**Статья 10** (Fair trial) | Denial of justice (*denial of justice*), institutional sabotage, and substitution of criminal procedure with administrative dead-ends. |
| **Historical Torture & Non-Rehabilitation** (Case 1-568/98) | **Статья 5** (Prohibition of torture)<br>**Статья 8** (Effective remedy) | Ongoing state failure to provide redress, maintaining a state of perpetual victimization (*continuing violations*). |

---

## ⚙️ Neo4j Cypher Integration

```cypher
// 1. Register UDHR Article 17 if not present
MERGE (hr17:HumanRight {number: "Статья 17", description: "Никто не должен быть произвольно лишен своего имущества"})

// 2. Link evidence from bank dossiers to UDHR Article 17
MATCH (doc:LegalDocument {filename: "20260414161715328.pdf"})
MERGE (doc)-[:PROVES_VIOLATION_OF]->(hr17);
```

---
*Authenticated via A©tor Key / TI-ULA / SHA-256 / Ed25519 Protocol.*
