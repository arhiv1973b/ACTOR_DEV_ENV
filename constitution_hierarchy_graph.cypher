// Cypher script to model the hierarchy of legal norms in TI-ULA Neo4j graph
MERGE (c4:Constitution {article: "Статья 4", description: "Приоритет и толкование по ВДПЧ"})
MERGE (c8:Constitution {article: "Статья 8", description: "Уважение международного права"})
MERGE (udhr:HumanRight {number: "UDHR 1948", status: "Jus Cogens"})
MERGE (un:InternationalNorm {name: "UN Charter", status: "Jus Cogens"})
MERGE (echr:Convention {name: "ECHR", status: "Secondary / Derivative"})

MERGE (udhr)-[:SUPREME_OVER]->(c4)
MERGE (un)-[:SUPREME_OVER]->(c8)
MERGE (c4)-[:SUPREME_OVER]->(echr)
MERGE (c8)-[:SUPREME_OVER]->(echr);
