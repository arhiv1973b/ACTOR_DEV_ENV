// Судебное определение первой инстанции
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

// Кассация
MERGE (cass:Cassation {
  cassation_id: "cassation-2022-03-10",
  date: date("2022-03-10"),
  grounds: "Nullity of acts contradicting jus cogens"
})
MERGE (cass)-[:CASSATES]->(ap)

// Верховный суд
MERGE (sc:Institution { name: "Supreme Court of Justice of Moldova", type: "SupremeCourt" })
MERGE (cass)-[:REVIEWED_BY]->(sc)

// Узел ВДПЧ
MERGE (udhr:LegalReference {
  source: "Universal Declaration of Human Rights",
  year: 1948,
  category: "UniversalStandard"
})

// Узел Венской конвенции
MERGE (vc:LegalReference {
  source: "Vienna Convention on the Law of Treaties",
  year: 1969,
  articles: "53,64",
  category: "Jus Cogens"
})

// Связи с международными нормами
MERGE (cass)-[:REFERENCES]->(udhr)
MERGE (cass)-[:REFERENCES]->(vc)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-full-chain-20220310" })
MERGE (ar)-[:VERIFIES]->(cd)
MERGE (ar)-[:VERIFIES]->(ap)
MERGE (ar)-[:VERIFIES]->(cass)
MERGE (ar)-[:TRACKS]->(sc)
MERGE (ar)-[:TRACKS]->(udhr)
MERGE (ar)-[:TRACKS]->(vc)
