// Cypher script to ingest A©tor-Shared inventory snapshot and deduplicate via MasterFile
CALL apoc.load.json("file:///shared_inventory.json") YIELD value AS row
WITH row

// 1. Создание единого Мастер-узла для каждого уникального хеша
MERGE (m:MasterFile {sha256: row.sha256})
ON CREATE SET m.sizeBytes = row.file_size,
              m.mimeType = row.mime_type,
              m.firstSeenPath = row.path,
              m.lastModified = row.last_modified

// 2. Создание узла физического расположения (Множества)
MERGE (f:FilePath {path: row.path})
SET f.lastModified = row.last_modified

// 3. Связывание пути с Мастер-файлом
MERGE (f)-[:IS_INSTANCE_OF]->(m)

// 4. Привязка к аудиторской сессии
MERGE (a:AuditSession {generated_at: "2026-05-16T14:36:14Z", protocol: "A©tor-Shared-Export"})
MERGE (m)-[:PROCESSED_IN]->(a);
