#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Run: python3 create_translations_zip.py
import os, io, zipfile

files = {
"en/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="en" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = FACTUAL PROOF — CASE MACHERET 1997–2026</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@600;900&display=swap" rel="stylesheet">
<style>
/* original site styles (truncated for brevity) */
/* Consolas rule required by protocol */
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; }
</style>
<meta name="description" content="Evidence portal — Case Maceret 1997–2026">
</head>
<body>
<nav id="actor-navigator" style="background:#070e16; border-bottom:2px solid #b8960c; padding:12px 20px; font-family:Consolas, 'Courier New', monospace; display:flex; justify-content:space-between; align-items:center;">
  <div style="display:flex; align-items:center; gap:15px;">
    <span style="color:#f0c040; font-weight:bold; letter-spacing:1px;">⚖️ A©t0r Integrity Engine v6.9</span>
    <span style="color:#666;">|</span>
    <span style="color:#d4cfc7; font-size:12px;">CONTOUR: <strong style="color:#ff4444;">H:\ACTOR_DEV_ENV</strong></span>
  </div>
  <div style="display:flex; gap:12px; font-size:12px;">
    <a href="index.html" style="color:#ffd700; text-decoration:none; padding:4px 8px; border:1px solid #2a2a2e; background:#111114;">[Core Vault]</a>
    <a href="evidence-roadmap.html" style="color:#e0e0e0; text-decoration:none; padding:4px 8px; border:1px solid #222;">[Roadmap]</a>
    <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0; text-decoration:none; padding:4px 8px; border:1px solid #222;">[Jus Cogens]</a>
    <a href="apostille-registry-fixed.html" style="color:#e0e0e0; text-decoration:none; padding:4px 8px; border:1px solid #222;">[Apostille Registry (90)]</a>
    <a href="un_contacts_copy_buttons.html" style="color:#4fc3f7; text-decoration:none; padding:4px 8px; border:1px solid #222;">[UN Liaison Contacts]</a>
  </div>
  <div style="font-size:11px; color:#ff6644; font-weight:bold; text-align: right; line-height: 1.2;">
    ⏱️ Over 10,000 days<br>
    <span style="color:#666; font-size:9px;">(1997-2026) continuous contour holding</span>
  </div>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// EVIDENTIARY ACT — MACHERET CASE 1997–2026</div>
    <div class="hero-title">From theory to practice:<br><em>Jus Cogens = Factual Proof</em></div>
    <div class="hero-subtitle">THE LOGIC OF A NORM WITHOUT LIMITATION · ERGA OMNES ACCOUNTABILITY</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> days of silence</span> <span class="eq-equals">=</span>
      <span class="eq-result">Erga Omnes violation</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">Key <em>Evidentiary Facts</em> — Not Allegations</div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">PROCEDURAL VACUUM</div><div class="ev-card-body"><span class="num num-auto">10,524</span> days without investigation</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">APOSTILLED ARCHIVE</div><div class="ev-card-body"><span class="num">90</span> apostilled documents. <strong>Evidence set preserved</strong></div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">FORGERY 15.03.2022</div><div class="ev-card-body"><strong>Fact:</strong> Nantoi Liudmila used Marcov I.M.'s identity in falsified records.</div></div>
  </div>

  <div class="verdict" style="border-color: var(--cyan); background: rgba(0, 184, 232, 0.05); margin-top: 40px;">
    <div class="verdict-title" style="color: var(--cyan); font-size: 1.2rem; text-align: center;">FUND LEGAL DEFENSE</div>
    <div class="verdict-body" style="text-align: center;">
      Direct secure routing for legal fund:<br><br>
      <strong style="font-family: var(--font-mono); font-size: 1.5em; color: var(--gold2); letter-spacing: 2px;">**** **** **** 6089</strong><br><br>
      <em style="color: var(--text2); font-size: 0.85em;">(Use strictly the destination card ending in 6089).</em>
    </div>
  </div>

</div>

<div class="div"></div>
<div class="footer">
  <span>CASE-MACHERET-1997–2026 · JUS COGENS PROOF DOCUMENT</span>
  <span>🔒 SHA-256 · INTEGRITY 100% · 2026</span>
</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>

</body>
</html>
""",

"ro/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="ro" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = PROBĂ FACTUALĂ — CAZUL MACHERET 1997–2026</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@600;900&display=swap" rel="stylesheet">
<style>
/* Consolas rule required by protocol */
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; }
</style>
</head>
<body>
<nav id="actor-navigator" style="background:#070e16; border-bottom:2px solid #b8960c; padding:12px 20px; font-family:Consolas, 'Courier New', monospace; display:flex; justify-content:space-between; align-items:center;">
  <div style="display:flex; align-items:center; gap:15px;">
    <span style="color:#f0c040; font-weight:bold; letter-spacing:1px;">⚖️ A©t0r Integrity Engine v6.9</span>
  </div>
  <div style="display:flex; gap:12px; font-size:12px;">
    <a href="index.html" style="color:#ffd700;">[Cutia Principală]</a>
    <a href="evidence-roadmap.html" style="color:#e0e0e0;">[Roadmap]</a>
    <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0;">[Jus Cogens]</a>
  </div>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// ACT PROBATOR — CAZUL MACHERET 1997–2026</div>
    <div class="hero-title">De la teorie la practică:<br><em>Jus Cogens = Dovadă Faptică</em></div>
    <div class="hero-subtitle">LOGICA NORMEI FĂRĂ PRESCRIPȚIE · RĂSPUNDERE ERGA OMNES</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> zile de tăcere</span> <span class="eq-equals">=</span>
      <span class="eq-result">Încălcare Erga Omnes</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">Fapte cheie <em>probatorii</em> — nu afirmații</div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">VID PROCEDURAL</div><div class="ev-card-body"><span class="num num-auto">10524</span> zile fără investigare</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">ARHIVĂ APOSTILATĂ</div><div class="ev-card-body"><span class="num">90</span> documente apostilate.</div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">FALS 15.03.2022</div><div class="ev-card-body"><strong>Fapt:</strong> Nantoi Liudmila a folosit identitatea falsificată.</div></div>
  </div>

  <div class="verdict">
    <div class="verdict-title">Concluzie: Jus Cogens = Dovadă Faptică</div>
    <div class="verdict-body">Impunerea neprovederii instituționale nu este o eroare judiciară. Este „cancerul” justiției.</div>
  </div>

</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>

</body>
</html>
""",

"es/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="es" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = PRUEBA FACTUAL — CASO MACHERET 1997–2026</title>
<style>
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; }
</style>
</head>
<body>
<nav style="background:#070e16; padding:12px 20px; font-family:Consolas, 'Courier New', monospace;">
  <div style="display:flex; gap:12px;">
    <a href="index.html" style="color:#ffd700;">[Bóveda Principal]</a>
    <a href="evidence-roadmap.html" style="color:#e0e0e0;">[Hoja de Ruta]</a>
    <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0;">[Jus Cogens]</a>
  </div>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// ACTA PROBATORIA — CASO MACHERET 1997–2026</div>
    <div class="hero-title">De la teoría a la práctica:<br><em>Jus Cogens = Prueba Fáctica</em></div>
    <div class="hero-subtitle">LA LÓGICA DE UNA NORMA SIN CADUCIDAD · RESPONSABILIDAD ERGA OMNES</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> días de silencio</span> <span class="eq-equals">=</span>
      <span class="eq-result">Violación Erga Omnes</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">Hechos clave <em>probatorios</em> — No alegaciones</div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">VACÍO PROCEDIMENTAL</div><div class="ev-card-body"><span class="num num-auto">10524</span> días sin investigación</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">ARCHIVO APOSTILLADO</div><div class="ev-card-body"><span class="num">90</span> documentos apostillados.</div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">FALSIFICACIÓN 15.03.2022</div><div class="ev-card-body"><strong>Hecho:</strong> Nantoi Liudmila empleó identidad falsificada.</div></div>
  </div>

  <div class="verdict">
    <div class="verdict-title">Conclusión: Jus Cogens = Prueba Fáctica</div>
    <div class="verdict-body">La impunidad institucional no es un fallo judicial. Es el "cáncer" de la justicia.</div>
  </div>
</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>
</body>
</html>
""",

"fr/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="fr" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = PREUVE FACTUELLE — AFFAIRE MACHERET 1997–2026</title>
<style>
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; }
</style>
</head>
<body>
<nav style="background:#070e16; padding:12px 20px; font-family:Consolas, 'Courier New', monospace;">
  <a href="index.html" style="color:#ffd700;">[Coffre Principal]</a>
  <a href="evidence-roadmap.html" style="color:#e0e0e0;">[Feuille de route]</a>
  <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0;">[Jus Cogens]</a>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// ACTE PROBATIF — AFFAIRE MACHERET 1997–2026</div>
    <div class="hero-title">De la théorie à la pratique:<br><em>Jus Cogens = Preuve Factuelle</em></div>
    <div class="hero-subtitle">LA LOGIQUE D'UNE NORME SANS PRESCRIPTION · RESPONSABILITÉ ERGA OMNES</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> jours de silence</span> <span class="eq-equals">=</span>
      <span class="eq-result">Violation Erga Omnes</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">Faits probants clés <em>— Pas des allégations</em></div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">VIDE PROCÉDURAL</div><div class="ev-card-body"><span class="num num-auto">10524</span> jours sans enquête</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">ARCHIVE APOSTILLÉE</div><div class="ev-card-body"><span class="num">90</span> documents apostillés.</div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">FALSIFICATION 15.03.2022</div><div class="ev-card-body"><strong>Fait :</strong> Nantoi Liudmila a utilisé une identité falsifiée.</div></div>
  </div>

  <div class="verdict">
    <div class="verdict-title">Conclusion: Jus Cogens = Preuve Factuelle</div>
    <div class="verdict-body">L'impunité institutionnelle n'est pas une erreur judiciaire. C'est le « cancer » de la justice.</div>
  </div>
</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>
</body>
</html>
""",

"zh/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="zh" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = 事实证据 — MACHERET 案 1997–2026</title>
<style>
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; }
</style>
</head>
<body>
<nav style="background:#070e16; padding:12px 20px; font-family:Consolas, 'Courier New', monospace;">
  <a href="index.html" style="color:#ffd700;">[核心库]</a>
  <a href="evidence-roadmap.html" style="color:#e0e0e0;">[路线图]</a>
  <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0;">[Jus Cogens]</a>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// 证据行为 — MACHERET 案 1997–2026</div>
    <div class="hero-title">从理论到实践：<br><em>Jus Cogens = 事实证据</em></div>
    <div class="hero-subtitle">无时效规范的逻辑 · ERGA OMNES 问责制</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> 天的沉默</span> <span class="eq-equals">=</span>
      <span class="eq-result">Erga Omnes 违反</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">关键 <em>证据事实</em></div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">程序真空</div><div class="ev-card-body"><span class="num num-auto">10524</span> 天未调查</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">已认证档案</div><div class="ev-card-body"><span class="num">90</span> 份加注认证的文件。</div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">伪造 2022-03-15</div><div class="ev-card-body"><strong>事实：</strong> Nantoi Liudmila 使用了伪造身份。</div></div>
  </div>

  <div class="verdict">
    <div class="verdict-title">结论：Jus Cogens = 事实证据</div>
    <div class="verdict-body">制度性不受惩罚并非司法错误。它是司法的“癌症”。</div>
  </div>
</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>
</body>
</html>
""",

"ru/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="ru" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = ФАКТИЧЕСКОЕ ДОКАЗАТЕЛЬСТВО — ДЕЛО MACHERET 1997–2026</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@600;900&display=swap" rel="stylesheet">
<style>
/* оригинальные стили оставлены. Добавлено правило Consolas согласно протоколу */
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; }
</style>
</head>
<body>
<nav id="actor-navigator" style="background:#070e16; border-bottom:2px solid #b8960c; padding:12px 20px; font-family:Consolas, 'Courier New', monospace; display:flex; justify-content:space-between; align-items:center;">
  <div style="display:flex; align-items:center; gap:15px;">
    <span style="color:#f0c040; font-weight:bold; letter-spacing:1px;">⚖️ A©t0r Integrity Engine v6.9</span>
  </div>
  <div style="display:flex; gap:12px; font-size:12px;">
    <a href="index.html" style="color:#ffd700;">[Core Vault]</a>
    <a href="evidence-roadmap.html" style="color:#e0e0e0;">[Roadmap]</a>
    <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0;">[Jus Cogens]</a>
  </div>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// ДОКАЗАТЕЛЬНЫЙ АКТ — ДЕЛО MACHERET 1997–2026</div>
    <div class="hero-title">От теории к практике:<br><em>Jus Cogens = Фактическое Доказательство</em></div>
    <div class="hero-subtitle">ЛОГИКА НОРМЫ БЕЗ СРОКА ДАВНОСТИ · ОТВЕТСТВЕННОСТЬ ERGA OMNES</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> суток молчания</span> <span class="eq-equals">=</span>
      <span class="eq-result">Нарушение Erga Omnes</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">Ключевые <em>доказательные факты</em></div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">ПРОЦЕССУАЛЬНЫЙ ВАКУУМ</div><div class="ev-card-body"><span class="num num-auto">10524</span> суток без расследования</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">АПОСТИЛИРОВАННЫЙ АРХИВ</div><div class="ev-card-body"><span class="num">90</span> документов апостилировано.</div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">ПОДЛОГ 15.03.2022</div><div class="ev-card-body"><strong>Факт:</strong> Nantoi Liudmila использовала подложную идентичность.</div></div>
  </div>

  <div class="verdict">
    <div class="verdict-title">Вывод: Jus Cogens = Фактическое доказательство</div>
    <div class="verdict-body">Институциональная безнаказанность — это не судебная ошибка. Это «рак» правосудия.</div>
  </div>
</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>
</body>
</html>
""",

# Arabic (RTL) version added per your request:
"ar/jus-cogens-proof-macheret.html": r"""<!DOCTYPE html>
<html lang="ar" dir="rtl" id="html-root">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JUS COGENS = دليل واقعي — قضية MACHERET 1997–2026</title>
<style>
/* Consolas rule required by protocol; basic RTL adjustments */
body, .f-field, .f-sha, .hero, .verdict { font-family: Consolas, "Courier New", monospace; direction: rtl; text-align: right; }
.hero-title em { font-style: italic; }
</style>
</head>
<body>
<nav id="actor-navigator" style="background:#070e16; border-bottom:2px solid #b8960c; padding:12px 20px; font-family:Consolas, 'Courier New', monospace; display:flex; justify-content:space-between; align-items:center;">
  <div style="display:flex; align-items:center; gap:15px;">
    <span style="color:#f0c040; font-weight:bold; letter-spacing:1px;">⚖️ A©t0r Integrity Engine v6.9</span>
  </div>
  <div style="display:flex; gap:12px; font-size:12px;">
    <a href="index.html" style="color:#ffd700; text-decoration:none; padding:4px 8px; border:1px solid #2a2a2e; background:#111114;">[المستودع الأساسي]</a>
    <a href="evidence-roadmap.html" style="color:#e0e0e0; text-decoration:none; padding:4px 8px; border:1px solid #222;">[خريطة الأدلة]</a>
    <a href="jus-cogens-proof-macheret.html" style="color:#e0e0e0; text-decoration:none; padding:4px 8px; border:1px solid #222;">[Jus Cogens]</a>
  </div>
  <div style="font-size:11px; color:#ff6644; font-weight:bold; text-align: left; line-height: 1.2;">
    ⏱️ أكثر من 10,000 يوم<br>
    <span style="color:#666; font-size:9px;">(1997-2026) استمرار الاحتفاظ بالمخطط</span>
  </div>
</nav>

<div class="wrap">
  <div class="hero">
    <div class="hero-eyebrow">// عمل إثباتي — قضية MACHERET 1997–2026</div>
    <div class="hero-title">من النظرية إلى التطبيق:<br><em>Jus Cogens = دليل واقعي</em></div>
    <div class="hero-subtitle">منطق قاعدة بلا تقادم · مسؤولية Erga Omnes</div>
    <div class="hero-equation">
      <span class="eq-part">Jus Cogens</span> <span class="eq-equals">+</span>
      <span class="eq-part"><span class="num num-auto">10524</span> يومًا من الصمت</span> <span class="eq-equals">=</span>
      <span class="eq-result">خرق Erga Omnes</span>
    </div>
  </div>

  <div class="sec-hd"><span class="sec-num">§ 03</span><div class="sec-title">الوقائع الإثباتية الرئيسية <em>— ليست ادعاءات</em></div></div>
  <div class="evidence-grid">
    <div class="ev-card"><div class="ev-card-icon">⏱</div><div class="ev-card-title">فراغ إجرائي</div><div class="ev-card-body"><span class="num num-auto">10524</span> يومًا دون تحقيق</div></div>
    <div class="ev-card"><div class="ev-card-icon">📂</div><div class="ev-card-title">أرشيف مصدق (Apostille)</div><div class="ev-card-body"><span class="num">90</span> وثيقة مصدقة.</div></div>
    <div class="ev-card"><div class="ev-card-icon">🧬</div><div class="ev-card-title">تزوير 15.03.2022</div><div class="ev-card-body"><strong>حقيقة:</strong> استخدمت Nantoi Liudmila هوية مزيفة في السجلات.</div></div>
  </div>

  <div class="verdict" style="border-color: var(--cyan); background: rgba(0, 184, 232, 0.05); margin-top: 40px;">
    <div class="verdict-title" style="color: var(--cyan); font-size: 1.2rem; text-align: center;">دعم الدفاع القانوني</div>
    <div class="verdict-body" style="text-align: center;">
      توجيه آمن ومباشر لصندوق الدفاع القانوني:<br><br>
      <strong style="font-family: var(--font-mono); font-size: 1.5em; color: var(--gold2); letter-spacing: 2px;">**** **** **** 6089</strong><br><br>
      <em style="color: var(--text2); font-size: 0.85em;">(استخدم بطاقة الوجهة المنتهية بـ 6089 حصراً).</em>
    </div>
  </div>

</div>

<div class="div"></div>
<div class="footer">
  <span>CASE-MACHERET-1997–2026 · JUS COGENS PROOF DOCUMENT</span>
  <span>🔒 SHA-256 · INTEGRITY 100% · 2026</span>
</div>

<script>
function updateDaysCounter() {
  const baseline = new Date('1997-08-06');
  const now = new Date();
  const diffTime = Math.abs(now - baseline);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.num-auto').forEach(el => {
    el.textContent = diffDays.toLocaleString();
  });
}
window.onload = updateDaysCounter;
</script>

</body>
</html>
"""
}

def ensure_dirs_and_write(tmp_dir="translations"):
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    for path, content in files.items():
        full = os.path.join(tmp_dir, path)
        d = os.path.dirname(full)
        if not os.path.exists(d):
            os.makedirs(d)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

def make_zip(zip_name="translations.zip", tmp_dir="translations"):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, filenames in os.walk(tmp_dir):
            for fn in filenames:
                fp = os.path.join(root, fn)
                arcname = os.path.relpath(fp, tmp_dir)
                z.write(fp, arcname)
    print("Created", zip_name)

if __name__ == "__main__":
    ensure_dirs_and_write()
    make_zip()
    print("Done. translations.zip contains the language folders: en, es, fr, ar, zh, ro, ru.")