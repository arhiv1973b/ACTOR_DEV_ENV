// Судебное определение первой инстанции
MERGE (cd:CourtDecision {
  case_no: "3-3107/2021",
  date: date("2021-12-30"),
  judge: "Tatiana Avasilae",
  sector: "Riscani Court",
  type: "Determination"
})

// Заявитель
MERGE (r:Recipient { name: "Macheret Alexei", status: "Applicant" })
MERGE (cd)-[:ADDRESSES]->(r)

// Апелляция заявителя
MERGE (ap:Appeal {
  appeal_id: "appeal-2022-01-15",
  date: date("2022-01-15"),
  grounds: "Violation of constitutional guarantees, disability rights, language rights"
})
MERGE (ap)-[:APPEALS]->(cd)
MERGE (r)-[:FILED]->(ap)

// Вышестоящий суд
MERGE (hc:Institution { name: "Chisinau Court of Appeal", type: "HigherCourt" })
MERGE (ap)-[:REVIEWED_BY]->(hc)

// Юридическая ссылка
MERGE (lr:LegalReference {
  source: "Vienna Convention 1969",
  articles: "53,64",
  category: "Jus Cogens"
})
MERGE (ap)-[:REFERENCES]->(lr)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-appeal-20220115" })
MERGE (ar)-[:VERIFIES]->(ap)
