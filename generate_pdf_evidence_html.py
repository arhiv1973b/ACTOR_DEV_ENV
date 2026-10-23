#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚖ [A©tor Declaration] Automated PDF Evidence HTML Generator (GitHub Pages Ready)
Generates case_evidence_report.html with absolute GitHub Pages URLs for online auditors.
"""

import os
import hashlib

BASE_URL = "https://arhiv1973b.github.io/ACTOR_DEV_ENV"

html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Комплексная доказательная база — Case Maceret (23.10.2026)</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f9f9f9; color: #333; line-height: 1.6; margin: 0; padding: 20px; }}
    .container {{ max-width: 950px; margin: auto; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    h1, h2, h3 {{ color: #1a365d; }}
    .stamp-box {{ background: #edf2f7; border-left: 4px solid #3182ce; padding: 15px; margin: 20px 0; font-family: monospace; }}
    .evidence-list {{ list-style-type: none; padding-left: 0; }}
    .evidence-list li {{ background: #fff; border: 1px solid #cbd5e0; margin-bottom: 20px; padding: 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
    .evidence-list a {{ color: #2b6cb0; text-decoration: none; font-weight: bold; font-size: 1.1em; }}
    .evidence-list a:hover {{ text-decoration: underline; }}
    .ocr-text {{ background: #f1f5f9; border: 1px dashed #cbd5e0; padding: 15px; margin: 15px 0 5px 0; border-radius: 4px; font-family: Consolas, monospace; font-size: 0.95em; color: #2d3748; white-space: pre-wrap; line-height: 1.4; }}
    .ocr-text pre {{ margin: 0; font-family: inherit; }}
    .footer {{ margin-top: 40px; font-size: 0.9em; color: #718096; border-top: 1px solid #e2e8f0; padding-top: 20px; text-align: center; }}
    .badge {{ display: inline-block; background: #2b6cb0; color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }}
    .highlight {{ background: #fffaf0; border-left: 4px solid #dd6b20; padding: 15px; margin: 20px 0; border-radius: 4px; }}
  </style>
</head>
<body>
<div class="container">
  <h1>Канонический процессуальный отчёт и доказательная база</h1>
  <p><span class="badge">Дата: 23 октября 2026 г.</span> <span class="badge">Статус: Зарегистрировано в Министерстве (Nr. 2597/26)</span></p>

  <div class="stamp-box">
    <h3>🛃 Официальный входящий штамп / Official Incoming Stamp</h3>
    <p><strong>Орган получения:</strong> MINISTERUL MUNCII ŞI PROTECŢIEI SOCIALE AL REPUBLICII MOLDOVA</p>
    <p><strong>Регистрационный номер:</strong> Nr. de intrare: 2597 / 26</p>
    <p><strong>Дата поступления:</strong> 23.10.2026</p>
    <p><strong>Субъект / Заявитель:</strong> Алексей Мачерет (Maceret Alexei)</p>
  </div>

  <div class="highlight">
    <h3>📌 Сводный процессуальный статус</h3>
    <p><strong>Алексей Мачерет:</strong> Бессрочная тяжёлая степень ограничения возможностей (<em>grad sever de dizabilitate fără termen</em>) на основании отчёта № 1232 от 05.04.2021.</p>
    <p><strong>Ирина Олейник (член семьи / сопровождающее лицо):</strong> Выраженная степень ограничения возможностей (<em>grad accentuat</em>), сертификат № <strong>CI2623797</strong> от 08.07.2026 (действителен до 01.07.2027, менеджер кейса: Moroz Larisa).</p>
    <p><strong>Суть инцидента:</strong> Неправомерное урезание социального пособия за октябрь 2026 года до 123.00 MDL вместо установленных 1167.84 MDL (признак финансового саботажа FinComBank).</p>
  </div>

  <h2>Постраничная опись и OCR-анализ пакета документов (GitHub Pages Online Links)</h2>
  <ul class="evidence-list">
    <li>
      <a href="{BASE_URL}/docs/page-1.png" target="_blank">📄 Лист 1 PDF — входящий штамп и запрос в Национальный консилиум</a>
      <div class="ocr-text"><pre>
Входящий штамп: Nr. de intrare 2597/26
Дата: 23.10.2026
Орган: Ministerul Muncii și Protecției Sociale
Запрос о разъяснении касательно выплаты социального пособия.
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-2.png" target="_blank">📄 Лист 2 PDF — решение о назначении пособия (Управление соц. обеспечения сектора Рышкань)</a>
      <div class="ocr-text"><pre>
Решение № A013794400034 от 14.08.2026
Назначено пособие: 1167.84 MDL/мес.
Действует до: 31.07.2027
Начальник: Violeta Dorul.
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-3.png" target="_blank">📄 Лист 3 PDF — подтверждение FinComBank (15.09.2026)</a>
      <div class="ocr-text"><pre>
Транзакция: 15.09.2026
Сумма: 1168.00 MDL
Статус: корректная выплата
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-4.png" target="_blank">📄 Лист 4 PDF — подтверждение FinComBank (15.10.2026)</a>
      <div class="ocr-text"><pre>
Транзакция: 15.10.2026
Сумма: 123.00 MDL
Статус: несоответствие установленному размеру (урезание)
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-5.png" target="_blank">📄 Лист 5 PDF — удостоверение личности (провизорное) Мачерета Алексея и вкладыш Олейник Ирины</a>
      <div class="ocr-text"><pre>
MACERET ALEXEI, IDNP: 2000001159655
Valabil: 03.04.2026 - 03.04.2027, ASP.
Fișa de însoțire: OLEINIC IRINA.
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-6.png" target="_blank">📄 Лист 6 PDF — United Nations House in Moldova и MRZ идентификации</a>
      <div class="ocr-text"><pre>
United Nations House in Moldova (131, 31 August 1989 st., Chisinau)
Контактные данные агентств ООН. Машиночитаемая зона документов.
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-7.png" target="_blank">📄 Лист 7 PDF — сертификат об инвалидности Олейник Ирины (Grad accentuat)</a>
      <div class="ocr-text"><pre>
Certificat nr. CI2623797 din 08.07.2026
Nume: OLEINIC IRINA, IDNP: 0971908038829
Grad de dizabilitate: Grad accentuat (01.07.2026 - 01.07.2027).
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-8.png" target="_blank">📄 Лист 8 PDF — удостоверения получателей социальных выплат</a>
      <div class="ocr-text"><pre>
Legitimatia beneficiarului de prestatie sociala
- Maceret Alexei
- Oleinic Irina
      </pre></div>
    </li>

    <li>
      <a href="{BASE_URL}/docs/page-9.png" target="_blank">📄 Лист 9 PDF — подтверждение Консилиума о бессрочной тяжелой степени Мачерета А.</a>
      <div class="ocr-text"><pre>
Raport nr. 1232 din 05.04.2021
Grad sever de dizabilitate fără termen.
Directo interimar: Stela PÎNZARU.
      </pre></div>
    </li>
  </ul>

  <div class="footer">
    <p><strong>A©TOR_KEY="# [⚖ A©tor Declaration]"</strong></p>
    <p>Канонический депозитарий: <code>ACTOR_DEV_ENV</code> | Merkle Root: <code>CFC9a2465bde77</code></p>
  </div>
</div>
</body>
</html>
"""

output_filename = "case_evidence_report.html"
lines = [l for l in html_content.splitlines() if "checksum:" not in l]
clean_text = "\n".join(lines)
file_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
final_html = clean_text + f"\n<!-- checksum: sha256({file_hash}) -->\n"

with open(output_filename, "w", encoding="utf-8", newline="\n") as f:
    f.write(final_html)

print(f"Generated GitHub Pages ready {output_filename}. SHA-256: {file_hash}")
