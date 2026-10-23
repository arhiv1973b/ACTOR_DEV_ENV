// 1. Регистрация сводного аналитического документа
MERGE (doc:LegalDocument {filename: "Блокировки со стороны - тех кто причастен к краже _Гуреев и Вакарчук.pdf"})
SET doc.type = "Executive Summary & Case Dossier",
    doc.date = "2026-08",
    doc.status = "VERIFIED_SYNTHESIS"

// 2. Связь с делом
WITH doc
MERGE (c:Case {name: "MACHERET-1997-2026"})
MERGE (doc)-[:BELONGS_TO]->(c)

// 3. Фиксация причастных лиц / объектов давления (на основе текста документа)
MERGE (gureev:Actor {name: "Гуреев", role: "State Official / Involved Party"})
MERGE (vacarciuc:Actor {name: "Андрей Вакарчук", role: "Inspectoratul de Poliție Râșcani Şef"})
MERGE (doc)-[:REFERENCES_OFFICIAL]->(gureev)
MERGE (doc)-[:REFERENCES_OFFICIAL]->(vacarciuc)

// 4. Связь с финансовым ущербом
WITH doc
MERGE (t:Transaction {hash: "c99741a242c72ac62a4725d13a494aac2568aa10917cc2d9be689bcf889053ce"})
MERGE (doc5:Evidence {description: "Сумма 25,210,256.15 MDL и блокировка счетов наследования"})
MERGE (doc)-[:DOCUMENTS_LOSS]->(doc5)
MERGE (doc5)-[:RELATED_TO_TX]->(t);
