// Unified Workflow Report with AuditSession integration
MATCH (t:Transaction)-[:ASSOCIATED_WITH]->(i:Image)
MATCH (t)-[:HAS_EVIDENCE_STATUS]->(es:EvidenceStatus)
OPTIONAL MATCH (i)-[:IS_INSTANCE_OF]->(m:MasterFile)
OPTIONAL MATCH (m)-[:PROCESSED_IN]->(a:AuditSession)
RETURN t.hash AS TransactionHash,
       t.amountMDL AS AmountMDL,
       i.fileName AS ImageFile,
       i.sha256 AS ImageSHA256,
       es.value AS EvidenceStatus,
       coalesce(m.binaryExists, true) AS BinaryExists,
       a.generated_at AS AuditSession,
       a.protocol AS Protocol;
