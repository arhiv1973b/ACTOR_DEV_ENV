// Судебное определение
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

// Институт: Рышкановский суд
MERGE (inst_court:Institution { name: "Riscani Court", type: "Court" })
MERGE (cd)-[:ISSUED_BY]->(inst_court)

// Институт: Венецианская комиссия
MERGE (inst_vc:Institution { name: "Venetian Commission", type: "Commission" })
MERGE (cd)-[:CHALLENGES]->(inst_vc)

// Юридическая ссылка
MERGE (lr:LegalReference { source: "Vienna Convention 1969", articles: "53,64", category: "Jus Cogens" })
MERGE (cd)-[:REFERENCES]->(lr)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-courtdecision-20211230" })
MERGE (ar)-[:VERIFIES]->(cd)
