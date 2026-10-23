// Aggregate transaction and image counts per AuditSession
MATCH (a:AuditSession)<-[:PROCESSED_IN]-(m:MasterFile)<-[:IS_INSTANCE_OF]-(i:Image)<-[:ASSOCIATED_WITH]-(t:Transaction)
RETURN a.generated_at AS AuditSession,
       a.protocol AS Protocol,
       count(DISTINCT t) AS TransactionCount,
       count(DISTINCT i) AS ImageCount
ORDER BY a.generated_at DESC;
