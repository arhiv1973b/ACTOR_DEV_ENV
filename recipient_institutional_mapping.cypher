// Привязка адресатов к типам института и юридическим ссылкам

// Судебные органы
MATCH (r:Recipient)
WHERE r.email ENDS WITH "@justice.md" OR r.email ENDS WITH "@csj.md" OR r.email ENDS WITH "@constcourt.md"
MERGE (c:Court {name:"Court"})
MERGE (r)-[:BELONGS_TO]->(c)
MERGE (udhr:LegalReference {article:"UDHR 17(2)", title:"Right to property"})
MERGE (const:LegalReference {article:"Constitution RM 4", title:"Supremacy of human rights"})
MERGE (c)-[:REFERENCES]->(udhr)
MERGE (c)-[:REFERENCES]->(const);

// Прокуратура
MATCH (r:Recipient)
WHERE r.email ENDS WITH "@procuratura.md"
MERGE (p:Prosecutor {name:"Prosecutor"})
MERGE (r)-[:BELONGS_TO]->(p)
MERGE (udhr:LegalReference {article:"UDHR 8", title:"Right to effective remedy"})
MERGE (const:LegalReference {article:"Constitution RM 4", title:"Supremacy of human rights"})
MERGE (p)-[:REFERENCES]->(udhr)
MERGE (p)-[:REFERENCES]->(const);

// Полиция
MATCH (r:Recipient)
WHERE r.email ENDS WITH "@igp.gov.md"
MERGE (pol:Police {name:"Police"})
MERGE (r)-[:BELONGS_TO]->(pol)
MERGE (udhr:LegalReference {article:"UDHR 5", title:"Prohibition of torture"})
MERGE (const:LegalReference {article:"Constitution RM 4", title:"Supremacy of human rights"})
MERGE (pol)-[:REFERENCES]->(udhr)
MERGE (pol)-[:REFERENCES]->(const);
