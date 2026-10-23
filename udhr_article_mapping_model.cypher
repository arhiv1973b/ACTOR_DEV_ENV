// Примеры материальных преступлений
UNWIND [
  {event:"BANK_FUNDS_BLOCKED", article:"17", text:"Право на собственность"},
  {event:"ILLEGAL_SURVEILLANCE", article:"12", text:"Право на неприкосновенность частной жизни"},
  {event:"ARBITRARY_DETENTION", article:"9", text:"Запрет произвольного ареста и задержания"},
  {event:"DENIAL_OF_FAIR_TRIAL", article:"10", text:"Право на справедливое судебное разбирательство"},
  {event:"TORTURE_OR_CRUEL_TREATMENT", article:"5", text:"Запрет пыток и жестокого обращения"}
] AS mapping

// Создание узлов CriminalEvent и их корреляция с UDHR
MERGE (ce:CriminalEvent { type: mapping.event })
MERGE (hr:HumanRight { number: "Статья " + mapping.article })
SET hr.text = mapping.text

MERGE (ce)-[:VIOLATES]->(hr)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-criminal-events-udhr" })
MERGE (ar)-[:TRACKS]->(ce)
MERGE (ar)-[:TRACKS]->(hr)
