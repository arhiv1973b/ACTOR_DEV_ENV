// 1. Создание узла процессуального документа (LegalDocument)
MERGE (doc:LegalDocument {
    id: "LEGAL_INSTR_8b3c9f1a",
    filename: "LEGAL_INSTRUCTIONS_GONCHAR_CHEBES_DRUTA_20260919.md",
    commit_hash: "8b3c9f1a",
    type: "Procedural Instructions",
    date: "2026-09-19"
})

// 2. Привязка к основному делу (Case)
WITH doc
MERGE (c:Case {name: "MACHERET-1997-2026"})
MERGE (doc)-[:BELONGS_TO]->(c)

// 3. Создание или обновление узлов адвокатов (Actors) и связывание их с документом
WITH doc, c
UNWIND [
    {name: "Василий Гончар", role: "Advocate"},
    {name: "Alexei Chebeș", role: "Advocate"},
    {name: "Борис Друцэ", role: "Advocate"}
] AS adv_data
MERGE (a:Actor {name: adv_data.name})
ON CREATE SET a.type = adv_data.role
MERGE (doc)-[:DIRECTED_TO]->(a)
MERGE (a)-[:REPRESENTATIVE_IN]->(c)

// 4. Привязка документа к отчету (Master Dashboard Report)
WITH doc
MERGE (report:LegalDocument {filename: "MASTER_DASHBOARD_REPORT.md"})
MERGE (doc)-[:BASED_ON]->(report);
