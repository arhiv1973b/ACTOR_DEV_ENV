// 1. Инициализация дела CASE-MACHERET-1997-2026
MERGE (c:Case {id: "CASE-MACHERET-1997-2026"})

// 2. Материальные криминальные события
MERGE (att:CriminalEvent {
  event_id: "attempt-2022-01-09",
  date: date("2022-01-09"),
  type: "Assassination Attempt",
  description: "Начало покушения"
})
MERGE (c)-[:CONTAINS_INCIDENT]->(att)

MERGE (murd:CriminalEvent {
  event_id: "murder-markova-2022-03-16",
  date: date("2022-03-16"),
  type: "Homicide",
  victim: "Маркова Галина Ивановна",
  description: "Убийство матери заявителя"
})
MERGE (c)-[:CONTAINS_INCIDENT]->(murd)
MERGE (att)-[:LED_TO]->(murd)

// 3. Универсальные стандарты: ВДПЧ и Венская конвенция (Jus Cogens)
MERGE (udhr:LegalReference {
  source: "Universal Declaration of Human Rights",
  year: 1948,
  category: "UniversalPeremptoryNorm"
})

MERGE (vc:LegalReference {
  source: "Vienna Convention on the Law of Treaties",
  year: 1969,
  articles: "53,64",
  category: "Jus Cogens"
})

// Прямая квалификация нарушений через ВДПЧ
MERGE (murd)-[:VIOLATES]->(udhr)
MERGE (murd)-[:BREACHES]->(vc)

// 4. Фиксация судебного саботажа и покрытия убийства (Denial of Justice)
MERGE (cd:CourtDecision {
  case_no: "3-3107/2021",
  date: date("2021-12-30"),
  judge: "Tatiana Avasilae",
  sector: "Riscani Court",
  type: "Determination"
})

// Связь между убийством и институциональным сокрытием/безнаказанностью
MERGE (murd)-[:CAUSED_BLOCKADE {
  status: "Denial of Justice",
  period: "2022-2026",
  description: "Использование процессуальных отказов для обеспечения безнаказанности"
}]->(cd)

// 5. Аудиторский трек
MERGE (ar:AuditRun { run_id: "audit-udhr-criminal-chain-2026" })
MERGE (ar)-[:VERIFIES]->(murd)
MERGE (ar)-[:VERIFIES]->(cd)
MERGE (ar)-[:TRACKS]->(udhr)
MERGE (ar)-[:TRACKS]->(vc)
