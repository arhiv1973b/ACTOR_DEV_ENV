// 1. Точечное сравнение двух версий статуса для одного адресата
MATCH (r:Recipient {name:$name})-[:HAS_STATUS|PREVIOUS_STATUS*]->(s:DeliveryStatus)
WHERE s.checked_at IN [$timeX, $timeY]
RETURN r.name AS Recipient,
       r.email AS Email,
       s.checked_at AS CheckedAt,
       s.sent AS Sent,
       s.delivered AS Delivered,
       s.acknowledged AS Acknowledged
ORDER BY s.checked_at ASC;

// 2. Автоматическое вычисление различий между двумя статусами
MATCH (r:Recipient {name:$name})-[:HAS_STATUS|PREVIOUS_STATUS*]->(s:DeliveryStatus)
WHERE s.checked_at IN [$timeX, $timeY]
WITH r, collect(s) AS statuses
WHERE size(statuses) = 2
WITH r, statuses[0] AS old, statuses[1] AS new
RETURN r.name AS Recipient,
       r.email AS Email,
       old.checked_at AS OldCheckedAt,
       new.checked_at AS NewCheckedAt,
       old.sent <> new.sent AS SentChanged,
       old.delivered <> new.delivered AS DeliveredChanged,
       old.acknowledged <> new.acknowledged AS AckChanged;
