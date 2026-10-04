// 1. Создание узлов международных наблюдателей (InternationalObserver)
MERGE (un:InternationalObserver {name: "OHCHR (United Nations)", type: "Global Monitor"})
MERGE (vc:InternationalObserver {name: "Venice Commission (CoE)", type: "Legal Monitor"})
MERGE (g7:InternationalObserver {name: "G7 Diplomatic Missions", type: "Diplomatic Monitor"})

// 2. Инициализация или поиск реестра доказательств
MERGE (ledger:EvidenceLedger {id: "Evidence_Ledger.json"})
ON CREATE SET ledger.created_at = timestamp(), ledger.integrity = "SHA-256 Validated"

// 3. Установка связей VERIFIED_BY (Ожидание независимого аудита)
MERGE (ledger)-[v_un:VERIFIED_BY]->(un)
ON CREATE SET v_un.status = "Pending Review", v_un.escalation_date = timestamp()

MERGE (ledger)-[v_vc:VERIFIED_BY]->(vc)
ON CREATE SET v_vc.status = "Pending Review", v_vc.escalation_date = timestamp()

MERGE (ledger)-[v_g7:VERIFIED_BY]->(g7)
ON CREATE SET v_g7.status = "Pending Review", v_g7.escalation_date = timestamp()

// 4. Привязка наблюдателей напрямую к делу и к юридическим нормам
MATCH (c:Case {id: "CASE-MACHERET-1997-2026"})
MERGE (c)-[:MONITORED_BY]->(un)
MERGE (c)-[:MONITORED_BY]->(vc)
MERGE (c)-[:MONITORED_BY]->(g7)

// 5. Связь нарушителей с наблюдателями (Эскалация)
MATCH (inst)-[:REFERENCES]->(u:LegalReference)
WHERE inst:Court OR inst:Prosecutor OR inst:Police
MERGE (inst)-[:ESCALATED_TO {reason: "Delivery Ignored / Sabotage Risk"}]->(un)
