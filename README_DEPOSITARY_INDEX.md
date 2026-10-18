# ACTOR_MASTER_EVIDENCE_PACKAGE (1997–2026)
**Framework:** TI-ULA (Transcendent Integrity - Universal Legal Architecture)  
**Subject:** A©tor (IDNP: 2000001159655)  
**Legal Standard:** Jus Cogens, Erga Omnes, Hague Convention 1961, ECHR Art. 3 & 5, ICCPR.

---

## Structure & Contents

```text
ACTOR_MASTER_EVIDENCE_PACKAGE_1997-2026/
│
├── 01_LEGAL_MEMORANDUM/
│   ├── ACTOR_MEMORANDUM_JUS_COGENS.pdf         # Финальный меморандум (ВДПЧ, Юс Когенс, Erga Omnes)
│   ├── LEGAL_STATEMENT_HAGUE_1961.md           # Декларация о прямом действии Гаагской конвенции 1961 г.
│   └── CONTEXT_MAP_1997_2026.json              # Историко-правовая матрица восстанавливаемой хронологии
│
├── 02_AUDIT_MATRICES/
│   ├── signature_audit_matrix.csv              # Таблица верификации рукописных подписей (Complex Manual Signature)
│   ├── audit_matrix_full.csv                   # Сводная матрица всех документов с SHA-256 и OCR-контекстом
│   └── registry_cross_reference.json           # Сверка 90+ записей реестра с официальными кодами
│
├── 03_GRAPH_GRAPHICS/
│   ├── signature_evidence_graph.dot            # Исходный DOT-скрипт графа связей
│   ├── signature_evidence_graph.svg            # Векторная рендер-схема (для публикации на зеркале и печати)
│   ├── signature_evidence_graph.png            # Растровая схема высокого разрешения
│   └── signature_audit_graph.json              # Граф-модель в формате JSON (Cytoscape/Neo4j)
│
├── 04_EVIDENCE_ARCHIVE/
│   ├── JUDICIAL_REHABILITATION_2009/           # Дело № 1ra-834/09 (ВСП РМ: полная отмена, освобождение)
│   │   ├── apostila_CG0T6Y1TBUEL7.pdf
│   │   └── vsp_decision_21_07_2009_ru.pdf
│   ├── CNDDCM_DISABILITY_RECORDS/              # Сертификат C013564402308 (Тяжелая инвалидность бессрочно)
│   │   ├── apostila_90VS71FRKM4S3.pdf
│   │   └── cnddcm_confirmation_stela_pinzaru.pdf
│   └── RAW_PDF_INDEX/                          # Индексированный массив оригиналов PDF
│
├── 05_CRYPTO_MANIFESTS/
│   ├── CHECKSUMS_SHA256.txt                    # Реестр SHA-256 хэшей всех файлов пакета
│   ├── CHECKSUMS_SHA256.txt.sig                # Цифровая подпись Ed25519 / GPG
│   ├── ACTOR_MANIFEST_SIGNATURE.json           # Подписанный A©tor-манифест целостности
│   └── GPG_PUBLIC_KEY.asc                      # Публичный ключ для автономной проверки подлинности
│
└── README_DEPOSITARY_INDEX.md                  # Главный сопроводительный паспорт пакета
```

## Verification & Integrity
- All evidence files are immutably anchored via SHA-256 hashes and signed under GPG/Ed25519.
- Verified against unlawful procedural obstacles, artificial IDNP transliteration collisions (`MACERET` vs `MACHERET`), and administrative concealments in Moldovan courts (Curtea de Apel Chișinău, Judecătoria Chișinău sediul Centru).
- Public Repository Mirror: `https://arhiv1973b.github.io/apostille-archive-english/`
