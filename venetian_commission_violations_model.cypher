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

// Институт: Венецианская комиссия
MERGE (inst_vc:Institution {
  name: "Venetian Commission",
  type: "Commission",
  status: "Challenged"
})

// Связи
MERGE (inst_vc)-[:CONTRADICTS]->(udhr)
MERGE (inst_vc)-[:VIOLATES]->(vc)
