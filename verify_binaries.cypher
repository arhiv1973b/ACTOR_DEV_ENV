// Cypher query to verify and flag missing physical binaries
MATCH (m:MasterFile)<-[:IS_INSTANCE_OF]-(f:FilePath)
// Note: In Neo4j APOC or APOC extensions, file existence can be checked, or processed via application layer.
// Here we set a property based on application check or path validation:
SET f.binaryExists = apoc.file.exists(f.path),
    m.binaryExists = apoc.file.exists(m.firstSeenPath);

// Return missing files
MATCH (m:MasterFile)<-[:IS_INSTANCE_OF]-(f:FilePath)
WHERE f.binaryExists = false
RETURN m.sha256 AS Hash, f.path AS MissingPath;
