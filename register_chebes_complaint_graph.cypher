// 1. Регистрация первичного процессуального документа
MERGE (doc:LegalDocument {filename: "Кебеш в отношении кражи.pdf"})
SET doc.type = "Plângere (Complaint)",
    doc.date = "2026-08-09",
    doc.amount_mdl = 25210256.15,
    doc.institution_target = "Procuratura municipiului Chișinău",
    doc.status = "FILED"

// 2. Привязка документа к основному делу
WITH doc
MERGE (c:Case {name: "MACHERET-1997-2026"})
MERGE (doc)-[:BELONGS_TO]->(c)

// 3. Привязка к автору (Адвокат Алексей Кебеш / Alexei Chebeș)
WITH doc
MERGE (a:Actor {name: "Alexei Chebeș"})
ON CREATE SET a.type = "Advocate"
MERGE (a)-[:AUTHORED]->(doc)

// 4. Связывание документа с финансовой транзакцией (c99741)
WITH doc
MATCH (t:Transaction) WHERE t.amountMDL = 25210256.15 OR t.hash = "c99741a242c72ac62a4725d13a494aac2568aa10917cc2d9be689bcf889053ce"
MERGE (doc)-[:PROVIDES_EVIDENCE_FOR]->(t)
SET t.legal_status = "SUBJECT_TO_COMPLAINT_ART_298_CPP"

// 5. Жесткая фиксация нарушений ВДПЧ (Статья 8 и Статья 10) на основе отказа государства
WITH doc, t
MERGE (hr8:HumanRight {number: "Статья 8"})
MERGE (hr10:HumanRight {number: "Статья 10"})
MERGE (doc)-[:PROVES_VIOLATION_OF]->(hr8)
MERGE (doc)-[:PROVES_VIOLATION_OF]->(hr10)
MERGE (t)-[:VIOLATES]->(hr10);
