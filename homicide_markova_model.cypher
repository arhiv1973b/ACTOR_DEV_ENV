// Пример события: убийство Марковой
MERGE (ce:CriminalEvent {
  id: "murder-markova-2022-03-16",
  type: "HOMICIDE",
  date: date("2022-03-16"),
  victim: "Galina Ivanovna Markova"
})

// Нарушение статьи ВДПЧ
MERGE (hr:HumanRight { number: "Статья 3", text: "Право на жизнь, свободу и личную неприкосновенность" })
MERGE (ce)-[:VIOLATES]->(hr)

// Ссылка на Венскую конвенцию
MERGE (vc:LegalReference {
  source: "Vienna Convention on the Law of Treaties",
  year: 1969,
  articles: "53,64",
  category: "Jus Cogens"
})
MERGE (ce)-[:REFERENCES]->(vc)

// Институция как соучастник
MERGE (inst:Institution { name: "Venetian Commission", type: "Commission", status: "Aggressor" })
MERGE (ce)-[:INSTIGATED_BY]->(inst)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-criminal-markova-20220316" })
MERGE (ar)-[:TRACKS]->(ce)
MERGE (ar)-[:TRACKS]->(hr)
MERGE (ar)-[:TRACKS]->(vc)
MERGE (ar)-[:TRACKS]->(inst)
