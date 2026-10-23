// Определение суда первой инстанции
MERGE (cd:CourtDecision {
  case_no: "3-3107/2021",
  date: date("2021-12-30"),
  judge: "Tatiana Avasilae",
  sector: "Riscani Court",
  type: "Determination"
})

// Апелляция
MERGE (ap:Appeal {
  appeal_id: "appeal-2022-01-15",
  date: date("2022-01-15"),
  grounds: "Violation of constitutional guarantees, disability rights, language rights"
})
MERGE (ap)-[:APPEALS]->(cd)

// Вышестоящий суд
MERGE (hc:Institution { name: "Chisinau Court of Appeal", type: "HigherCourt" })
MERGE (ap)-[:REVIEWED_BY]->(hc)

// Кассационная жалоба
MERGE (cass:Cassation {
  cassation_id: "cassation-2022-03-10",
  date: date("2022-03-10"),
  grounds: "Nullity of acts contradicting jus cogens, Vienna Convention 1969"
})
MERGE (cass)-[:CASSATES]->(ap)

// Верховный суд
MERGE (sc:Institution { name: "Supreme Court of Justice of Moldova", type: "SupremeCourt" })
MERGE (cass)-[:REVIEWED_BY]->(sc)

// Юридическая ссылка
MERGE (lr:LegalReference {
  source: "Vienna Convention 1969",
  articles: "53,64",
  category: "Jus Cogens"
})
MERGE (cass)-[:REFERENCES]->(lr)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-cassation-20220310" })
MERGE (ar)-[:VERIFIES]->(cass)
