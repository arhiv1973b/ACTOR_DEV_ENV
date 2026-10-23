// Обновление статуса эскалации после успешной маршрутизации msmtp
MATCH (ledger:EvidenceLedger {id: "Evidence_Ledger.json"})-[v:VERIFIED_BY]->(obs:InternationalObserver)
SET v.status = "DISPATCHED",
    v.dispatch_timestamp = timestamp(),
    v.manifest_reference = "payloads_manifest.sha256"
RETURN obs.name AS Observer, v.status AS EscalationStatus, v.dispatch_timestamp AS Timestamp;
