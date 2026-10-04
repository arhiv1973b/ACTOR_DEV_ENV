// CourtDecision → Recipient → Institution → LegalReference
MERGE (cd:CourtDecision {
  case_no: "3-3107/2021",
  date: date("2021-12-30"),
  judge: "Tatiana Avasilae",
  sector: "Riscani Court"
})
MERGE (r:Recipient { name: "Macheret Alexei" })
MERGE (inst:Institution { name: "Riscani Court", type: "Court" })
MERGE (lr:LegalReference { source: "Vienna Convention 1969", article: "53,64" })

MERGE (cd)-[:ADDRESSES]->(r)
MERGE (cd)-[:ISSUED_BY]->(inst)
MERGE (cd)-[:REFERENCES]->(lr)

// Дополнительно: связь с AuditRun
MERGE (ar:AuditRun { run_id: "audit-2021-12-30" })
MERGE (ar)-[:VERIFIES]->(cd)
