// Analytic Cypher Queries for TI-ULA Graph

// 1. Find files with multiple physical instances (duplicates)
MATCH (m:MasterFile)<-[:IS_INSTANCE_OF]-(f:FilePath)
WITH m, collect(f.path) AS paths, count(f) AS instances
WHERE instances > 1
RETURN m.sha256 AS Hash,
       m.sizeBytes AS Size,
       instances AS DuplicateCount,
       paths AS FilePaths
ORDER BY DuplicateCount DESC;

// 2. Filter system duplicates (e.g. desktop.ini)
MATCH (m:MasterFile)<-[:IS_INSTANCE_OF]-(f:FilePath)
WHERE f.path CONTAINS "desktop.ini"
RETURN m.sha256 AS Hash, collect(f.path) AS Paths;

// 3. Aggregate unique MasterFile counts per AuditSession
MATCH (m:MasterFile)-[:PROCESSED_IN]->(a:AuditSession)
RETURN a.generated_at AS AuditSession,
       a.protocol AS Protocol,
       count(m) AS UniqueMasterFiles
ORDER BY a.generated_at DESC;
