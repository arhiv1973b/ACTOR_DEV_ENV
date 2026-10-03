// ============================================================================
// NEO4J CYPHER SCRIPT: USURPATION & HUMAN RIGHTS VIOLATION GRAPH MODEL
// Protocol: TI-ULA / A©tor Protocol (Case Macheret / Case O)
// ============================================================================

// 1. Constitution Articles (Republic of Moldova)
MERGE (:ConstitutionArticle {number:"2", title:"Узурпация государственной власти"});

// 2. Universal Declaration of Human Rights (UDHR) Nodes
MERGE (:HumanRight {number:"5", title:"Запрет пыток и жестокого обращения"});
MERGE (:HumanRight {number:"8", title:"Право на эффективное средство правовой защиты"});
MERGE (:HumanRight {number:"10", title:"Право на справедливое судебное разбирательство"});
MERGE (:HumanRight {number:"12", title:"Неприкосновенность жилища и частной жизни"});
MERGE (:HumanRight {number:"17", title:"Право собственности"});

// 3. Evidence Nodes (Case O / Macheret)
MERGE (:Evidence {case:"O", description:"Рейдерский захват, блокировка правосудия, хищение средств"});
MERGE (:Evidence {case:"FinComBank", description:"Финансовое удушение и ограничение доступа к счетам до 180 леев"});
MERGE (:Evidence {case:"CyberTerror", description:"Аппаратный саботаж и реальный киберхарассмент (выборочная блокировка клавиш)"});

// 4. Relationships: Evidence -> Constitution Article (Usurpation)
MATCH (c:ConstitutionArticle {number:"2"}), (e:Evidence {case:"O"})
MERGE (e)-[:USURPS]->(c);

// 5. Relationships: Evidence -> Human Rights Violations (UDHR)
MATCH (h:HumanRight {number:"17"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h);

MATCH (h:HumanRight {number:"5"}), (e:Evidence {case:"CyberTerror"})
MERGE (e)-[:VIOLATES]->(h);

MATCH (h:HumanRight {number:"8"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h);

MATCH (h:HumanRight {number:"10"}), (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(h);

MATCH (h:HumanRight {number:"12"}), (e:Evidence {case:"FinComBank"})
MERGE (e)-[:VIOLATES]->(h);
