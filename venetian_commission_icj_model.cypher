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

// Институт: Венецианская комиссия (оспариваемая роль)
MERGE (inst_vc:Institution {
  name: "Venetian Commission",
  type: "Commission",
  status: "Aggressor"
})
MERGE (cd)-[:CHALLENGES]->(inst_vc)

// Международное дело (ICJ 2012 Germany v. Italy and Greece)
MERGE (icj:LegalCase {
  case_name: "Germany v. Italy and Greece",
  court: "International Court of Justice",
  year: 2012
})
MERGE (inst_vc)-[:INVOLVED_IN]->(icj)

// Юридическая ссылка
MERGE (lr:LegalReference {
  source: "Vienna Convention 1969",
  articles: "53,64",
  category: "Jus Cogens"
})
MERGE (cd)-[:REFERENCES]->(lr)

// Интеграция в аудит
MERGE (ar:AuditRun { run_id: "audit-institution-vc-2012" })
MERGE (ar)-[:VERIFIES]->(cd)
MERGE (ar)-[:TRACKS]->(inst_vc)
