// 1. Link GitHub Issue 9 to Transaction c99741
MERGE (i:GitHubIssue {number: 9})
SET i.title = "Safe-Commit Protocol Integration",
    i.state = "closed",
    i.integrity_lock = "AIPS-2025"
WITH i
MATCH (t:Transaction {TransactionHash: "c99741a242c72ac62a4725d13a494aac2568aa10917cc2d9be689bcf889053ce"})
MERGE (i)-[:ANCHORS]->(t);

// 2. Aggregate GitHub Issues and linked artifacts for Master Dashboard
MATCH (i:GitHubIssue)
OPTIONAL MATCH (i)-[:ANCHORS|LINKED_TO]->(artifact)
RETURN i.number AS IssueNumber,
       i.title AS Title,
       i.state AS State,
       count(artifact) AS LinkedArtifacts,
       collect(coalesce(artifact.TransactionHash, artifact.SessionID))[0..3] AS SampleArtifacts
ORDER BY i.number DESC;
