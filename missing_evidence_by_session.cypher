// Aggregate missing transactions and master files by AuditSession
MATCH (a:AuditSession)<-[:PROCESSED_IN]-(m:MasterFile)<-[:IS_INSTANCE_OF]-(i:Image)<-[:ASSOCIATED_WITH]-(t:Transaction)
WHERE coalesce(m.binaryExists, true) = false
RETURN a.generated_at AS AuditSession,
       a.protocol AS Protocol,
       count(DISTINCT t) AS MissingTransactions,
       count(DISTINCT m) AS MissingMasterFiles,
       count(DISTINCT i) AS MissingImages
ORDER BY a.generated_at DESC;
