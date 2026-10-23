// Master Dashboard Report combining Transactions, Images, Binary Existence, and AuditSession
MATCH (t:Transaction)-[:ASSOCIATED_WITH]->(i:Image)
MATCH (t)-[:HAS_EVIDENCE_STATUS]->(es:EvidenceStatus)
MATCH (t)-[:HAS_LEGAL_CHARACTERIZATION]->(lc:LegalCharacterization)
OPTIONAL MATCH (i)-[:IS_INSTANCE_OF]->(m:MasterFile)
OPTIONAL MATCH (m)-[:PROCESSED_IN]->(a:AuditSession)
RETURN t.hash AS TransactionHash,
       t.amountMDL AS AmountMDL,
       i.fileName AS ImageFile,
       i.sha256 AS ImageSHA256,
       es.value AS EvidenceStatus,
       lc.value AS LegalCharacterization,
       coalesce(m.binaryExists, true) AS BinaryExists,
       coalesce(a.generated_at, 'N/A') AS AuditSession,
       coalesce(a.protocol, 'N/A') AS Protocol;
