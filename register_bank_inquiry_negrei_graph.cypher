// 1. Регистрация официального запроса в FinComBank и банковских выписок
MERGE (doc1:LegalDocument {filename: "20260414161715328.pdf"})
SET doc1.type = "Bank App Interface & Formal Inquiry (25.2M MDL)",
    doc1.date = "2026-04-09",
    doc1.status = "VERIFIED_EVIDENCE"

MERGE (doc2:LegalDocument {filename: "20260414160348300.pdf"})
SET doc2.type = "Complaint Art. 298 CPP (Avc. Nicolae Negrei & Proc. Ciuperca)",
    doc2.date = "2026-06-19",
    doc2.status = "VERIFIED_PROCEDURAL_RECORD"

// 2. Связь с делом
WITH doc1, doc2
MATCH (c:Case {name: "MACHERET-1997-2026"})
MERGE (doc1)-[:BELONGS_TO]->(c)
MERGE (doc2)-[:BELONGS_TO]->(c)

// 3. Привязка адвоката Николая Негрея к графу
MERGE (negrei:Actor {name: "Nicolae Negrei", role: "Advocate"})
MERGE (doc2)-[:AUTHORED]->(negrei)
MERGE (negrei)-[:REPRESENTATIVE_IN]->(c)

// 4. Связь с финансовой транзакцией и фиксация нарушения Статьи 8 ВДПЧ (Non-rehabilitation / Effective remedy)
WITH doc1, doc2
MATCH (t:Transaction {hash: "c99741a242c72ac62a4725d13a494aac2568aa10917cc2d9be689bcf889053ce"})
MERGE (hr8:HumanRight {number: "Статья 8"})
MERGE (doc1)-[:DOCUMENTS_DISCREPANCY]->(t)
MERGE (doc2)-[:PROVES_VIOLATION_OF]->(hr8);
