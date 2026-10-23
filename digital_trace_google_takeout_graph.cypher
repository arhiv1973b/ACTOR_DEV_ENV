// 1. Создание узлов цифровых следов (DigitalTrace) на основе парсинга Google Takeout / Bank Logs
UNWIND [
  {
    logId: "trace_auth_001",
    timestamp: "2026-04-03T10:53:15Z", 
    ip_address: "192.168.x.x",
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    action_type: "UNAUTHORIZED_LOGIN",
    account: "arhiv240@gmail.com",
    description: "Несанкционированный вход в аккаунт до момента транзакции"
  },
  {
    logId: "trace_otp_002",
    timestamp: "2026-04-03T10:55:12Z", 
    ip_address: "192.168.x.x",
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    action_type: "OTP_DELETED",
    account: "arhiv240@gmail.com",
    description: "Удаление входящего письма с OTP-кодом / уведомлением от FinComBank"
  },
  {
    logId: "trace_filter_003",
    timestamp: "2026-04-03T10:56:00Z",
    ip_address: "192.168.x.x",
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    action_type: "FILTER_CREATED",
    account: "arhiv240@gmail.com",
    description: "Настройка скрытого фильтра для перехвата банковских извещений"
  }
] AS trace

MERGE (dt:DigitalTrace {logId: trace.logId})
SET dt.timestamp = trace.timestamp,
    dt.ip_address = trace.ip_address,
    dt.user_agent = trace.user_agent,
    dt.action_type = trace.action_type,
    dt.account = trace.account,
    dt.description = trace.description;

// 2. Корреляция: Связываем цифровые диверсии с транзакцией c99741
MATCH (t:Transaction {hash: "c99741a242c72ac62a4725d13a494aac2568aa10917cc2d9be689bcf889053ce"})
MATCH (login:DigitalTrace {action_type: "UNAUTHORIZED_LOGIN"})
MATCH (delete:DigitalTrace {action_type: "OTP_DELETED"})
MATCH (filter:DigitalTrace {action_type: "FILTER_CREATED"})

MERGE (login)-[:FACILITATED_EXPROPRIATION]->(t)
MERGE (delete)-[:CONCEALED_EVIDENCE_OF]->(t)
MERGE (filter)-[:CONCEALED_EVIDENCE_OF]->(t);
