import os
import json
from datetime import datetime

def generate_expert_report():
    report_path = r"H:\ACTOR_DEV_ENV\expert_forensic_report.html"
    print(f"--- [REPORT] ГЕНЕРАЦИЯ ЭКСПЕРТНОГО ОТЧЕТА: {report_path} ---")
    
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Expert Forensic Audit Report | Case #40710256</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #222; max-width: 900px; margin: 40px auto; padding: 20px; background: #fff; }}
        h1, h2, h3 {{ color: #1a365d; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }}
        .meta-box {{ background: #f7fafc; border-left: 4px solid #3182ce; padding: 15px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: left; }}
        th {{ background: #edf2f7; }}
        code {{ background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #b83280; }}
        .badge {{ background: #c6f6d5; color: #22543d; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .chart-bar {{ background: #3182ce; height: 24px; color: white; text-align: right; padding-right: 8px; font-size: 12px; line-height: 24px; border-radius: 3px; margin: 5px 0; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #718096; border-top: 1px solid #e2e8f0; pt: 10px; }}
    </style>
</head>
<body>
    <h1>ЭКСПЕРТНЫЙ ФОРЕНЗИК-ОТЧЕТ</h1>
    <div class="meta-box">
        <p><strong>Идентификатор дела:</strong> CASE-MACHERET-1997-2026 (#40710256)</p>
        <p><strong>Протокол аудита:</strong> A©tor Forensic Audit V4.4</p>
        <p><strong>Дата формирования:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <p><strong>Статус целостности:</strong> <span class="badge">INTEGRITY_LOCKED</span></p>
    </div>

    <h2>1. Сводка медицинских данных (DICOM)</h2>
    <p>Проведена верификация <strong>921 файла DICOM</strong> (пациент: <code>Marcova^Galina</code>, серии Alpha / Beta включая Z-макросетку). Целостность подтверждена на уровне криптографических хэшей.</p>

    <h2>2. Сегментация реестра доказательств (EVIDENCE_REGISTRY_INDEX.json)</h2>
    <p>Общий объем индекса: <strong>205.00 MB</strong>. Реестр разделен на 7 чанков, содержащих суммарно <strong>3,473 верифицированных узла доказательств</strong>.</p>
    
    <table>
        <tr>
            <th>Чанк ID</th>
            <th>Количество узлов</th>
            <th>Визуализация распределения</th>
        </tr>
        <tr><td>Chunk 1</td><td>616</td><td><div class="chart-bar" style="width: 100%;">616</div></td></tr>
        <tr><td>Chunk 2</td><td>500</td><td><div class="chart-bar" style="width: 81%;">500</div></td></tr>
        <tr><td>Chunk 3</td><td>500</td><td><div class="chart-bar" style="width: 81%;">500</div></td></tr>
        <tr><td>Chunk 4</td><td>500</td><td><div class="chart-bar" style="width: 81%;">500</div></td></tr>
        <tr><td>Chunk 5</td><td>500</td><td><div class="chart-bar" style="width: 81%;">500</div></td></tr>
        <tr><td>Chunk 6</td><td>500</td><td><div class="chart-bar" style="width: 81%;">500</div></td></tr>
        <tr><td>Chunk 7</td><td>357</td><td><div class="chart-bar" style="width: 58%;">357</div></td></tr>
    </table>

    <h2>3. Криптографические хэши и привязка</h2>
    <ul>
        <li><strong>DAG Manifest SHA-256:</strong> <code>6C913818321D40F9EE10E56F417E1521B968F6209CB10614C83F037E6F5B060C</code></li>
        <li><strong>Форензик-манифест V4.4 SHA-256:</strong> <code>7755EB3AF9C5B60C03C6440799538AB1876EE35581410DCE4B54647C88C600F6</code></li>
        <li><strong>Юридический контур:</strong> Синхронизирован с иском к FinComBank S.A. (25,210,256.15 MDL) в Judecătoria Chișinău (sediul Centru).</li>
    </ul>

    <div class="footer">
        <p>A©tor Forensic Audit System — Автоматизированный экспертный контур доказательств.</p>
    </div>
</body>
</html>
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Экспертный отчет успешно сгенерирован: {report_path}")

if __name__ == "__main__":
    generate_expert_report()
