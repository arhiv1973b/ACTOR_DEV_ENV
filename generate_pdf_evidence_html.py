#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚖ [A©tor Declaration] Secure Automated PDF Evidence HTML Generator (GitHub Pages Ready with .jpg)
"""

import os
import re
import hashlib
import tempfile

BASE_URL = "https://arhiv1973b.github.io/ACTOR_DEV_ENV"


def mask_data(text: str) -> str:
    """Masks sensitive personal data such as IDNP (13-digit numbers)."""
    if not text:
        return text
    idnp_pattern = re.compile(r"\b(\d{6})(\d{7})\b")
    return idnp_pattern.sub(r"\1*******", text)


def generate_report():
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Комплексная доказательная база — Case Maceret (23.10.2026)</title>
  <style>
    :root {{
      --primary-blue: #0056b3;
      --light-blue: #e7f1ff;
      --text-dark: #333;
    }}

    body {{
      font-family: 'Segoe UI', Tahoma, sans-serif;
      color: var(--text-dark);
      line-height: 1.6;
      background: #f9f9f9;
      margin: 0;
      padding: 20px;
    }}

    .container {{
      max-width: 950px;
      margin: auto;
      background: #fff;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}

    .report-header {{
      background-color: var(--primary-blue);
      color: white;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 20px;
    }}

    h1, h2, h3 {{
      color: var(--primary-blue);
    }}

    .stamp-box {{
      background: var(--light-blue);
      border-left: 5px solid var(--primary-blue);
      padding: 15px;
      margin: 20px 0;
      font-family: monospace;
      border-radius: 0 8px 8px 0;
    }}

    .evidence-card {{
      border: 1px solid var(--light-blue);
      border-left: 5px solid var(--primary-blue);
      padding: 15px;
      margin-bottom: 15px;
      background: #f9fbff;
      border-radius: 0 8px 8px 0;
    }}

    .evidence-list {{
      list-style-type: none;
      padding-left: 0;
    }}

    .evidence-list a {{
      color: var(--primary-blue);
      text-decoration: none;
      font-weight: bold;
      font-size: 1.1em;
    }}

    .evidence-list a:hover {{
      text-decoration: underline;
    }}

    .ocr-text {{
      background: #f1f5f9;
      border: 1px dashed #cbd5e0;
      padding: 15px;
      margin: 15px 0 5px 0;
      border-radius: 4px;
      font-family: Consolas, monospace;
      font-size: 0.95em;
      color: #2d3748;
      white-space: pre-wrap;
      line-height: 1.4;
    }}

    .ocr-text pre {{
      margin: 0;
      font-family: inherit;
    }}

    .footer {{
      margin-top: 40px;
      font-size: 0.9em;
      color: #718096;
      border-top: 1px solid #e2e8f0;
      padding-top: 20px;
      text-align: center;
    }}

    .badge {{
      display: inline-block;
      background: var(--primary-blue);
      color: #fff;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.85em;
    }}

    .highlight {{
      background: #fffaf0;
      border-left: 4px solid #dd6b20;
      padding: 15px;
      margin: 20px 0;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
<div class="container">
  <div class="report-header">
    <h1>Канонический процессуальный отчёт и доказательная база</h1>
    <p><span class="badge" style="background:#fff; color:var(--primary-blue);">Дата: 23 октября 2026 г.</span> <span class="badge" style="background:#fff; color:var(--primary-blue);">Статус: Зарегистрировано в Министерстве (Nr. 2597/26)</span></p>
  </div>

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
    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-1.jpg" target="_blank">📄 Лист 1 PDF — входящий штамп и запрос в Национальный консилиум</a>
      <div class="ocr-text"><pre>{mask_data("Входящий штамп: Nr. de intrare 2597/26\nДата: 23.10.2026\nОрган: Ministerul Muncii și Protecției Sociale\nЗапрос о разъяснении касательно выплаты социального пособия.")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-2.jpg" target="_blank">📄 Лист 2 PDF — решение о назначении пособия (Управление соц. обеспечения сектора Рышкань)</a>
      <div class="ocr-text"><pre>{mask_data("Решение № A013794400034 от 14.08.2026\nНазначено пособие: 1167.84 MDL/мес.\nДействует до: 31.07.2027\nНачальник: Violeta Dorul.")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-3.jpg" target="_blank">📄 Лист 3 PDF — подтверждение FinComBank (15.09.2026)</a>
      <div class="ocr-text"><pre>{mask_data("Транзакция: 15.09.2026\nСумма: 1168.00 MDL\nСтатус: корректная выплата")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-4.jpg" target="_blank">📄 Лист 4 PDF — подтверждение FinComBank (15.10.2026)</a>
      <div class="ocr-text"><pre>{mask_data("Транзакция: 15.10.2026\nСумма: 123.00 MDL\nСтатус: несоответствие установленному размеру (урезание)")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-5.jpg" target="_blank">📄 Лист 5 PDF — удостоверение личности (провизорное) Мачерета Алексея и вкладыш Олейник Ирины</a>
      <div class="ocr-text"><pre>{mask_data("MACERET ALEXEI, IDNP: 2000001159655\nValabil: 03.04.2026 - 03.04.2027, ASP.\nFișa de însoțire: OLEINIC IRINA, IDNP: 0971908038829.")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-6.jpg" target="_blank">📄 Лист 6 PDF — United Nations House in Moldova и MRZ идентификации</a>
      <div class="ocr-text"><pre>{mask_data("United Nations House in Moldova (131, 31 August 1989 st., Chisinau)\nКонтактные данные агентств ООН. Машиночитаемая зона документов.")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-7.jpg" target="_blank">📄 Лист 7 PDF — сертификат об инвалидности Олейник Ирины (Grad accentuat)</a>
      <div class="ocr-text"><pre>{mask_data("Certificat nr. CI2623797 din 08.07.2026\nNume: OLEINIC IRINA, IDNP: 0971908038829\nGrad de dizabilitate: Grad accentuat (01.07.2026 - 01.07.2027).")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-8.jpg" target="_blank">📄 Лист 8 PDF — удостоверения получателей социальных выплат</a>
      <div class="ocr-text"><pre>{mask_data("Legitimatia beneficiarului de prestatie sociala\n- Maceret Alexei (IDNP: 2000001159655)\n- Oleinic Irina (IDNP: 0971908038829)")}</pre></div>
    </li>

    <li class="evidence-card">
      <a href="{BASE_URL}/docs/page-9.jpg" target="_blank">📄 Лист 9 PDF — подтверждение Консилиума о бессрочной тяжелой степени Мачерета А.</a>
      <div class="ocr-text"><pre>{mask_data("Raport nr. 1232 din 05.04.2021\nGrad sever de dizabilitate fără termen.\nDirector interimar: Stela PÎNZARU.")}</pre></div>
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

    lines = [l for l in html_template.splitlines() if "checksum:" not in l]
    clean_text = "\n".join(lines)
    file_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    final_html = clean_text + f"\n<!-- checksum: sha256({file_hash}) -->\n"

    output_filename = "case_evidence_report.html"
    dir_name = os.path.dirname(os.path.abspath(output_filename)) or "."

    with tempfile.NamedTemporaryFile(
        "w", dir=dir_name, delete=False, encoding="utf-8", newline="\n"
    ) as tf:
        tf.write(final_html)
        temp_name = tf.name

    os.replace(temp_name, output_filename)
    print(
        f"Atomically generated {output_filename} with .jpg assets. SHA-256: {file_hash}"
    )


if __name__ == "__main__":
    generate_report()
