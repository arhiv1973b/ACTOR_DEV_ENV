// Aggregate missing binary files per AuditSession
MATCH (a:AuditSession)<-[:PROCESSED_IN]-(m:MasterFile)<-[:IS_INSTANCE_OF]-(i:Image)
WHERE m.binaryExists = false
RETURN a.generated_at AS AuditSession,
       a.protocol AS Protocol,
       count(DISTINCT m) AS MissingMasterFiles,
       count(DISTINCT i) AS MissingImages
ORDER BY a.generated_at DESC;
