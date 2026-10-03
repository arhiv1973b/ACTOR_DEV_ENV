// ============================================================================
// NEO4J CYPHER SCRIPT: ULTIMATE UNIFIED USURPATION & DIGITAL TRACE GRAPH MODEL
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
MATCH (e:Evidence {case:"O"})
MERGE (e)-[:VIOLATES]->(:HumanRight {number:"5"})
MERGE (e)-[:VIOLATES]->(:HumanRight {number:"8"})
MERGE (e)-[:VIOLATES]->(:HumanRight {number:"10"})
MERGE (e)-[:VIOLATES]->(:HumanRight {number:"12"})
MERGE (e)-[:VIOLATES]->(:HumanRight {number:"17"});

// Узлы DigitalTrace (технические артефакты)
MERGE (:DigitalTrace {type:"OTP_DELETED", description:"Удаление OTP-кодов"});
MERGE (:DigitalTrace {type:"PROPERTY_SEIZED", description:"Рейдерский захват квартиры"});
MERGE (:DigitalTrace {type:"CYBER_HARASSMENT", description:"Психологический террор и киберхарассмент"});
MERGE (:DigitalTrace {type:"BANK_FUNDS_BLOCKED", description:"Искусственное ограничение доступа к счетам"});
MERGE (:DigitalTrace {type:"ILLEGAL_SURVEILLANCE", description:"Попытка установки аппаратных жучков"});
MERGE (:DigitalTrace {type:"QUESTION_MARK_BLOCKED", description:"Блокировка символа '?' как подавление права на вопросы и оспаривание решений по ст. 313 УПК РМ"});

// Связи Evidence ↔ DigitalTrace
MATCH (e:Evidence {case:"O"}), (dt:DigitalTrace {type:"OTP_DELETED"})
MERGE (e)-[:EVIDENCES]->(dt);

MATCH (e:Evidence {case:"O"}), (dt:DigitalTrace {type:"PROPERTY_SEIZED"})
MERGE (e)-[:EVIDENCES]->(dt);

MATCH (e:Evidence {case:"O"}), (dt:DigitalTrace {type:"CYBER_HARASSMENT"})
MERGE (e)-[:EVIDENCES]->(dt);

MATCH (e:Evidence {case:"O"}), (dt:DigitalTrace {type:"BANK_FUNDS_BLOCKED"})
MERGE (e)-[:EVIDENCES]->(dt);

MATCH (e:Evidence {case:"O"}), (dt:DigitalTrace {type:"ILLEGAL_SURVEILLANCE"})
MERGE (e)-[:EVIDENCES]->(dt);

MATCH (e:Evidence {case:"O"}), (dt:DigitalTrace {type:"QUESTION_MARK_BLOCKED"})
MERGE (e)-[:EVIDENCES]->(dt);

// Прямая квалификация нарушения для блокировки вопросительного знака
MATCH (dt:DigitalTrace {type:"QUESTION_MARK_BLOCKED"}), (h:HumanRight {number:"10"})
MERGE (dt)-[:VIOLATES]->(h);
