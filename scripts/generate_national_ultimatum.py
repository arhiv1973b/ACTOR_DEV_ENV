#!/usr/bin/env python3
"""
A©tor National Procedural Notices Generator
CASE-MACHERET-1997-2026 | TI-ULA

Reads proofs/manifest.json + proofs/un_evidence_bundle.json
and produces a bilingual (RO/RU) national procedural document:
docs/procedural/NATIONAL_ULTIMATUM_GP_RM_2026.md
"""

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "proofs" / "manifest.json"
BUNDLE_PATH = REPO_ROOT / "proofs" / "un_evidence_bundle.json"
OUTPUT_DIR = REPO_ROOT / "docs" / "procedural"
OUTPUT_PATH = OUTPUT_DIR / "NATIONAL_ULTIMATUM_GP_RM_2026.md"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sha_table(files: list) -> str:
    rows = []
    for f in files:
        rows.append(
            f"| `{f['id']}` | `{f['sha256']}` | {f['size_bytes']} | {f.get('date', '—')} |"
        )
    header = "| Artifact ID | SHA-256 | Size (bytes) | Date |\n|-------------|---------|--------------|------|"
    return header + "\n" + "\n".join(rows)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = load_json(MANIFEST_PATH)
    bundle = load_json(BUNDLE_PATH) if BUNDLE_PATH.exists() else {}

    subject = manifest.get("subject", {})
    repo = manifest.get("repository", {})
    files = manifest.get("files", [])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    case_id = manifest.get("case_id", "CASE-MACHERET-1997-2026")
    actor_key = manifest.get("actor_key", "# [⚖ A©tor Declaration]")
    idnp = subject.get("idnp", "2000001159655")
    full_name_ru = subject.get("full_name_ru", "Мачерет Алексей Артурович")
    full_name_en = subject.get("full_name_en", "Alexei Macheret / A©tor")

    sha_block = sha_table(files)
    repo_url = repo.get(
        "html_url", "https://github.com/arhiv1973b/maceret-case-evidence"
    )

    md = f"""# NOTIFICARE PROCESUALĂ / ПРОЦЕССУАЛЬНОЕ УВЕДОМЛЕНИЕ  
## {case_id}

**A©TOR_KEY:** `{actor_key}`  

---

### ADRESAT / АДРЕСАТЫ

1. **Procuratura Generală a Republicii Moldova** / Генеральная прокуратура Республики Молдова  
2. **Organul de urmărire penală** / Орган уголовного преследования  
3. **Avocatul Poporului (Ombudsmanul RM)** / Народный адвокат (Омбудсмен РМ)

---

### SUBIECT / СУБЪЕКТ

**{full_name_ru}**  
**{full_name_en}**  
**IDNP:** `{idnp}`  
Cetățean al Republicii Moldova / Гражданин Республики Молдова

---

### TEMĂ / ТЕМА

Restabilirea imediată a drepturilor încălcate prin reținerea ilegală a sumei de **25 210 256,15 MDL** de către KБ «FinComBank» АО,  
încetarea practicii de substituire a IDNP-ului legal și asigurarea unui remediu efectiv conform art. 5, 6, 7, 8 și 17 ale Declarației Universale a Drepturilor Omului (1948).

Восстановление немедленно нарушенных прав путём незаконного удержания суммы **25 210 256,15 MDL** КБ «FinComBank» АО,  
прекращение практики подмены законного IDNP и обеспечение эффективного средства правовой защиты в соответствии со ст. 5, 6, 7, 8 и 17 Всеобщей декларации прав человека (1948).

---

### 1. CERINȚĂ / ТРЕБОВАНИЕ 1  
**Reluarea / redeschiderea imediată a materialelor privind reținerea ilegală a activelor**

Se solicită:

- redeschiderea / reînceperea verificării / urmăririi penale privind faptele de reținere ilegală a sumei de **25 210 256,15 MDL** de către KБ «FinComBank» АО;
- anexarea obligatorie la dosar a următoarelor probe:
  - Răspunsul oficial al băncii **№ 6647/Out din 26.08.2026** (recunoașterea expresă a persoanei «Мачерет Алексей (Alexei Macheret)» și a IDNP `{idnp}`);
  - Avizul științific **№ 269 din 01.10.2026** al Institutului de Filologie (echivalența antroponimică MACERET ≡ MACHERET);
  - Decizia Curții Supreme de Justiție a RM din **21.07.2009**;
  - pachetul de probe înregistrat în depozitul imutabil GitHub (a se vedea secțiunea 4).

**Требуется:**

- немедленное возобновление / возбуждение проверки / уголовного производства по факту незаконного удержания суммы **25 210 256,15 MDL** КБ «FinComBank» АО;
- обязательное приобщение к материалам:
  - официального ответа банка **№ 6647/Out от 26.08.2026** (прямое признание лица «Мачерет Алексей (Alexei Macheret)» и IDNP `{idnp}`);
  - научного заключения **Aviz № 269 от 01.10.2026** Института филологии (антропонимическая эквивалентность MACERET ≡ MACHERET);
  - решения Высшей судебной палаты РМ от **21.07.2009**;
  - пакета доказательств, зафиксированного в неизменяемом GitHub-репозитории (см. раздел 4).

---

### 2. CERINȚĂ / ТРЕБОВАНИЕ 2  
**Emiterea unei soluții procesuale cu obligarea băncii de a prezenta traseul SWIFT MT103/UETR**

Se solicită emiterea unei soluții procesuale (ordonanță / demers) prin care:

- KБ «FinComBank» АО să fie obligată să prezinte în termen de 10 zile lucrătoare:
  - traseul complet SWIFT MT103 / UETR aferent sumei de 25 210 256,15 MDL;
  - extrasele de cont interne și de tranzit;
  - orice documente de compliance / AML invocate pentru reținerea fondurilor.

**Требуется вынесение процессуального решения (постановление / ходатайство), которым:**

- КБ «FinComBank» АО обязуется в 10-дневный срок представить:
  - полную трассировку SWIFT MT103 / UETR по сумме 25 210 256,15 MDL;
  - внутренние и транзитные выписки по счетам;
  - любые документы compliance / AML, на которые ссылается банк при удержании средств.

---

### 3. CERINȚĂ / ТРЕБОВАНИЕ 3  
**Încetarea practicii de folosire a IDNP-urilor fantomă și fixarea definitivă a IDNP-ului legal**

Se solicită:

- interzicerea oricărei utilizări a identificatorilor fantomă în locul IDNP-ului legal `{idnp}`;
- emiterea de către Agenția Servicii Publice (ASP) a unei confirmări oficiale că **unicul identificator valabil** al persoanei este IDNP `{idnp}`;
- actualizarea tuturor registrelor de stat (inclusiv cele bancare, judiciare și de stare civilă) cu acest identificator exclusiv.

**Требуется:**

- прекращение любой практики использования фантомных идентификаторов вместо законного IDNP `{idnp}`;
- выдача Агентством государственных услуг (ASP) официального подтверждения, что **единственным действительным идентификатором** лица является IDNP `{idnp}`;
- актуализация всех государственных реестров (включая банковские, судебные и акты гражданского состояния) с использованием исключительно этого идентификатора.

---

### 4. BLOC DE VERIFICARE A INTEGRITĂȚII / БЛОК ВЕРИФИКАЦИИ ЦЕЛОСТНОСТИ

Toate probele sunt înregistrate într-un depozit imutabil (DAG) cu verificări criptografice SHA-256:

**Repository:** [{repo_url}]({repo_url})  
**Branch:** `main`  
**Manifest version:** {manifest.get("manifest_version", "1.2.0")}  
**Case ID:** `{case_id}`

#### Tabelul sumelor de control SHA-256 (cheie de prevenire a sabotaajului / «pierderii» materialelor)

{sha_block}

Orice modificare ulterioară a fișierelor este detectabilă prin scriptul `scripts/validate_sha256.py` și prin GitHub Actions workflow.

Любое последующее изменение файлов обнаруживается скриптом `scripts/validate_sha256.py` и GitHub Actions workflow.

---

### 5. TEMEI JURIDIC / ПРАВОВОЕ ОСНОВАНИЕ

- Declarația Universală a Drepturilor Omului (1948) — articolele 5, 6, 7, 8 și 17 / Всеобщая декларация прав человека (1948) — ст. 5, 6, 7, 8 и 17;
- Pactul Internațional cu Privire la Drepturile Civile și Politice (ICCPR) / Международный пакт о гражданских и политических правах;
- Norme imperative Jus Cogens și obligații Erga Omnes / Императивные нормы Jus Cogens и обязательства Erga Omnes;
- Mandatele Procedurilor Speciale ONU (Referință: tw57lryb).

---

*Document generated under A©TOR_KEY = "{actor_key}"*  
*Date: {now}*  
*CASE-MACHERET-1997-2026*
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[OK] National Ultimatum generated: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
