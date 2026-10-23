// 1. Создание статей ВДПЧ с описаниями
MERGE (hr3:HumanRight {number: "Статья 3", description: "Право на жизнь, свободу и личную неприкосновенность"})
MERGE (hr8:HumanRight {number: "Статья 8", description: "Право на эффективное восстановление в правах компетентными судами"})
MERGE (hr9:HumanRight {number: "Статья 9", description: "Запрет произвольного ареста или задержания"})
MERGE (hr17:HumanRight {number: "Статья 17", description: "Никто не должен быть произвольно лишен своего имущества"})

// 2. Создание узла Транзакции c99741 с полным анкерингом
MERGE (t:Transaction {hash: "c99741a242c72ac62a4725d13a494aac2568aa10917cc2d9be689bcf889053ce"})
  SET t.dateTime = "2026-04-03T10:55:00",
      t.sender = "FinComBank S.A.",
      t.receiver = "Moldindconbank S.A.",
      t.amountMDL = 25210256.15,
      t.amountUSD = 1400000,
      t.walletToken = "MD-APPLEPAY-6089-20260403",
      t.dagNodeHash = "890fd87ad197e6158c8e184bed0250bb58f96b7c70556d65e4b58474ab99ade4",
      t.gitCommit = "50730561",
      t.githubRelease = "https://github.com/arhiv1973b/apostille-mirror/releases/tag/evidence-c99741-corrected-20260403",
      t.integrityLock = "AIPS-2025"

// 3. Связь транзакции с нарушенными статьями ВДПЧ
MERGE (t)-[:VIOLATES]->(hr3)
MERGE (t)-[:VIOLATES]->(hr8)
MERGE (t)-[:VIOLATES]->(hr9)
MERGE (t)-[:VIOLATES]->(hr17);
