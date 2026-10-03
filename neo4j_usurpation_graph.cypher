// ============================================================================
// NEO4J CYPHER SCRIPT: UNIFIED USURPATION & HUMAN RIGHTS VIOLATION GRAPH MODEL
// Protocol: TI-ULA / A©tor Protocol (Case Macheret / Case O)
// ============================================================================

// Узел Конституции РМ — Статья 2
MERGE (:ConstitutionArticle {number:"2", title:"Узурпация государственной власти"});

// Узлы ВДПЧ
MERGE (:HumanRight {number:"5", title:"Запрет пыток и жестокого обращения"});
MERGE (:HumanRight {number:"8", title:"Право на эффективное средство правовой защиты"});
MERGE (:HumanRight {number:"10", title:"Право на справедливый суд"});
MERGE (:HumanRight {number:"12", title:"Неприкосновенность жилища и частной жизни"});
MERGE (:HumanRight {number:"17", title:"Право собственности"});

// Узел доказательства (дело O)
MERGE (:Evidence {case:"O", description:"Рейдерский захват, блокировка правосудия, хищение средств, психологический террор"});

// Связь узурпации власти
MATCH (c:ConstitutionArticle {number:"2"}), (e:Evidence {case:"O"})
MERGE (e)-[:USURPS]->(c);

// Связи нарушений ВДПЧ
MATCH (h5:HumanRight {number:"5"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h5);

MATCH (h8:HumanRight {number:"8"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h8);

MATCH (h10:HumanRight {number:"10"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h10);

MATCH (h12:HumanRight {number:"12"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h12);

MATCH (h17:HumanRight {number:"17"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h17);
