// ============================================================
// NEO4J CYPHER SCRIPT: Legal Framework & OCR Findings Graph Import
// Scope: CASE-MACHERET-1997-2026
// Legal Basis: UDHR (Articles 3, 5, 8, 25) + Constitution of Moldova (Article 4)
// ============================================================

// 1. Инициализация фундаментальных правовых узлов (L0: Invariant)
MERGE (udhr:LegalFramework {name: "UDHR", alias: "ВДПЧ", priority: "Jus Cogens"})
MERGE (constMD:LegalFramework {name: "Constitution MD", priority: "National Supreme"})

MERGE (udhr3:Article {name: "UDHR Art. 3", description: "Right to life, liberty, and security"})
MERGE (udhr5:Article {name: "UDHR Art. 5", description: "Prohibition of torture and economic strangulation"})
MERGE (udhr8:Article {name: "UDHR Art. 8", description: "Right to an effective remedy"})
MERGE (udhr25:Article {name: "UDHR Art. 25", description: "Right to an adequate standard of living"})
MERGE (const4:Article {name: "Constitution MD Art. 4", description: "Priority of international law"})

// Установка иерархии правовых норм
MERGE (udhr3)-[:PART_OF]->(udhr)
MERGE (udhr5)-[:PART_OF]->(udhr)
MERGE (udhr8)-[:PART_OF]->(udhr)
MERGE (udhr25)-[:PART_OF]->(udhr)
MERGE (const4)-[:PART_OF]->(constMD)

WITH udhr, constMD // Разделитель контекста транзакции

// 2. Загрузка и парсинг JSON с результатами OCR
CALL apoc.load.json("file:///legal_findings_contextual.json") YIELD value
UNWIND keys(value) AS filename
WITH filename, value[filename] AS docData

// 3. Создание узлов доказательств (Evidence)
MERGE (doc:Evidence {id: filename})
SET doc.type = "OCR_Document",
    doc.processed = true,
    doc.dates = docData.dates

WITH doc, docData

// 4. Связывание документов со статьями на основе найденных паттернов (matches)
UNWIND docData.matches AS term

// Линковка к ст. 4 Конституции РМ
FOREACH (ignoreMe IN CASE WHEN term =~ '(?i).*(Art\\.?\\s*4\\s*Конституци).*' THEN [1] ELSE [] END |
    MATCH (a:Article {name: "Constitution MD Art. 4"})
    MERGE (doc)-[:INVOKES_LEGAL_BASIS]->(a)
)

// Линковка к статьям ВДПЧ
FOREACH (ignoreMe IN CASE WHEN term =~ '(?i).*(Art\\.?\\s*3).*' THEN [1] ELSE [] END |
    MATCH (a:Article {name: "UDHR Art. 3"})
    MERGE (doc)-[:VIOLATION_CLAIM]->(a)
)
FOREACH (ignoreMe IN CASE WHEN term =~ '(?i).*(Art\\.?\\s*5).*' THEN [1] ELSE [] END |
    MATCH (a:Article {name: "UDHR Art. 5"})
    MERGE (doc)-[:VIOLATION_CLAIM]->(a)
)
FOREACH (ignoreMe IN CASE WHEN term =~ '(?i).*(Art\\.?\\s*8).*' THEN [1] ELSE [] END |
    MATCH (a:Article {name: "UDHR Art. 8"})
    MERGE (doc)-[:VIOLATION_CLAIM]->(a)
)
FOREACH (ignoreMe IN CASE WHEN term =~ '(?i).*(Art\\.?\\s*25).*' THEN [1] ELSE [] END |
    MATCH (a:Article {name: "UDHR Art. 25"})
    MERGE (doc)-[:VIOLATION_CLAIM]->(a)
)

// Индикаторы норм высшего порядка (Jus Cogens / Erga Omnes)
FOREACH (ignoreMe IN CASE WHEN term =~ '(?i).*(Jus\\s*Cogens|Erga\\s*Omnes).*' THEN [1] ELSE [] END |
    MATCH (fw:LegalFramework {name: "UDHR"})
    MERGE (doc)-[:INVOKES_ABSOLUTE_NORM]->(fw)
);
