# 📦 Release: ACTOR_MASTER_EVIDENCE_PACKAGE_1997‑2026

**Tag:** `v1.0-ACTOR-AUDIT`  
**Branch:** `feature/cyber-sabotage-audit-10-2026`  
**Jurisdiction:** Jus Cogens & Erga Omnes  

---

## 🔑 Основные компоненты

### Audit Matrices & Protocols
- `MASTER_DOSSIER_INTUITIVE_AUDIT_MATRIX.md` — классификация VALID и DEFECTIVE узлов.
- `FINAL_AUDIT_SUMMARY_CONST_RM.md` — итоговый правовой фундамент (Конституция РМ, ВДПЧ, Гаагская конвенция).
- `EVIDENCE_CHAIN_VALIDATION.md` — сопоставление физических подписей с обезличенными записями реестра.

### Graphviz Visualizations
- `audit_graph_full.dot` — полный граф VALID vs DEFECTIVE узлов (13 архивных случаев).
- `signature_evidence_graph.dot` — слой физической подписи, показывающий разрыв цепочки.

### Cryptographic Anchors
- `CHECKSUMS_SHA256.txt` — контрольные суммы всех PDF и артефактов.
- Подписанные коммиты GPG/Ed25519 под декларацией **A©tor**.

### Cold Storage
- Архивы вынесены локально и исключены через `.gitignore` для оптимизации GitHub.
- Доступны в отдельном депозитарии при необходимости международной проверки.

### Automation
- `finalize_repo.sh` — скрипт финализации: очистка субмодуля, фиксация изменений, rewrite email‑метаданных, push.
- CI/CD workflows: `crypto_manifest_sync.yml`, `ti_ula_crypto_pipeline.yml`.

---

## ⚖️ Юридический фундамент
- **Статья 4 Конституции РМ** — верховенство международного права.
- **ВДПЧ (ст. 6, 8, 10, 28)** — признание правосубъектности, восстановление в правах, справедливый суд, международный порядок.
- **Гаагская конвенция 1961 г. (ст. 3, 5)** — обязательность идентификации подписи и должности.
- **Jus Cogens & Erga Omnes** — абсолютная недействительность институциональных подлогов.

---

## 📋 Для аудиторов
- **Что смотреть первым:**
  - `FINAL_AUDIT_SUMMARY_CONST_RM.md` — правовой базис.
  - `audit_graph_full.dot` — визуализация дефектов.
  - `EVIDENCE_CHAIN_VALIDATION.md` — доказательства физических подписей.
- **Как проверять:**
  - Сверить SHA‑256 хэши с `CHECKSUMS_SHA256.txt`.
  - Проверить подписи коммитов GPG.
  - Сопоставить PDF‑апостили с матрицей VALID/DEFECTIVE.

---

## 📎 References & Downloads
- 📄 [MASTER_AUDIT.pdf — презентационное досье](https://github.com/arhiv1973b/ACTOR_DEV_ENV/releases/download/v1.0-ACTOR-AUDIT/MASTER_AUDIT.pdf)
- 📄 [FINAL_AUDIT_SUMMARY_CONST_RM.md](https://github.com/arhiv1973b/ACTOR_DEV_ENV/blob/feature-cyber-sabotage-audit-10-2026/FINAL_AUDIT_SUMMARY_CONST_RM.md)
- 📄 [EVIDENCE_CHAIN_VALIDATION.md](https://github.com/arhiv1973b/ACTOR_DEV_ENV/blob/feature-cyber-sabotage-audit-10-2026/EVIDENCE_CHAIN_VALIDATION.md)
- 📊 [audit_graph_full.dot](https://github.com/arhiv1973b/ACTOR_DEV_ENV/blob/feature-cyber-sabotage-audit-10-2026/03_GRAPH_GRAPHICS/audit_graph_full.dot)
- 📊 [signature_evidence_graph.dot](https://github.com/arhiv1973b/ACTOR_DEV_ENV/blob/feature-cyber-sabotage-audit-10-2026/03_GRAPH_GRAPHICS/signature_evidence_graph.dot)
- 🔐 [CHECKSUMS_SHA256.txt](https://github.com/arhiv1973b/ACTOR_DEV_ENV/blob/feature-cyber-sabotage-audit-10-2026/CHECKSUMS_SHA256.txt)

---
✅ Репозиторий чист, синхронизирован и готов к международному применению.
