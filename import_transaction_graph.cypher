LOAD CSV WITH HEADERS FROM 'file:///transaction_image_map.csv' AS row

// Узел транзакции
MERGE (t:Transaction {hash: row.TransactionHash})
  SET t.dateTime = row.DateTime,
      t.sender = row.Sender,
      t.receiver = row.Receiver,
      t.amountMDL = toFloat(row.AmountMDL),
      t.amountUSD = toFloat(row.AmountUSD),
      t.walletToken = row.WalletToken,
      t.cardConflict = row.CardConflict,
      t.case = row.Case

// Узел изображения
MERGE (i:Image {sha256: row.SHA256})
  SET i.fileName = row.ImageFile,
      i.localPath = row.LocalPath,
      i.sizeBytes = toInteger(row.SizeBytes)

// Узлы метаданных дела
MERGE (lc:LegalCharacterization {value: row.LegalCharacterization})
MERGE (es:EvidenceStatus {value: row.EvidenceStatus})
MERGE (rs:RecordStatus {value: row.RecordStatus})

// Узлы workflow‑шагов
MERGE (s1:WorkflowStep {step: "Step1_SaveManifest"})
MERGE (s2:WorkflowStep {step: "Step2_RegisterToDAG", dagNode: row.DAGNode})
MERGE (s3:WorkflowStep {step: "Step3_SignCommit", integrityLock: "AIPS-2025"})
MERGE (s4:WorkflowStep {step: "Step4_GitHubRelease", releaseUrl: row.GitHubRelease})

// Узел релиза
MERGE (r:Release {url: row.GitHubRelease})

// Связи транзакции и доказательства
MERGE (t)-[:ASSOCIATED_WITH]->(i)
MERGE (t)-[:HAS_LEGAL_CHARACTERIZATION]->(lc)
MERGE (t)-[:HAS_EVIDENCE_STATUS]->(es)
MERGE (t)-[:HAS_RECORD_STATUS]->(rs)

// Связи workflow
MERGE (i)-[:PROCESSED_BY_WORKFLOW]->(s1)
MERGE (s1)-[:NEXT]->(s2)
MERGE (s2)-[:NEXT]->(s3)
MERGE (s3)-[:NEXT]->(s4)
MERGE (s2)-[:REGISTERED_IN_DAG {nodeHash: row.DAGNode}]->(i)
MERGE (s4)-[:ANCHORED_AT]->(r);

// Выбор всех транзакций со статусом UNVERIFIED
MATCH (t:Transaction)-[:HAS_EVIDENCE_STATUS]->(es:EvidenceStatus {value: "UNVERIFIED_UNTIL_PRIMARY_SOURCE_CHECK"})
MATCH (t)-[:ASSOCIATED_WITH]->(i:Image)
RETURN t.hash AS TransactionHash,
       t.dateTime AS DateTime,
       t.sender AS Sender,
       t.receiver AS Receiver,
       es.value AS EvidenceStatus,
       i.fileName AS ImageFile,
       i.sha256 AS SHA256,
       i.localPath AS LocalPath,
       i.sizeBytes AS SizeBytes;
