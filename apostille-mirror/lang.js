(function () {
  const translations = {
    ru: {
      'portal-title': 'ПОРТАЛ ДОКАЗАТЕЛЬСТВ И МАСТЕР-ХРАНИЛИЩЕ',
      'portal-subtitle': 'Криптографическая фиксация и защита Jus Cogens / Erga Omnes норм.',
      'nav-core': 'Ядро хранилища',
      'nav-chronology': 'Хронология',
      'nav-jus': 'Jus Cogens',
      'nav-theft': 'Доказательства кражи',
      'nav-mosaic': 'HTML-мозаика',
      'evidence-nodes': 'ДОКАЗАТЕЛЬНЫЕ УЗЛЫ',
      'navigation': 'НАВИГАЦИЯ',
      'integrity': 'ПРОВЕРКА ЦЕЛОСТНОСТИ',
      'site-status': 'Статус: Проверено ✓',
      'portal-foot': 'CASE-MACHERET-1997-2026 | Master Evidence Archive',
      'lang': 'Язык',
      'mosaic-title': 'Мозаика HTML-доказательств',
      'mosaic-subtitle': 'Разрешённый локальный просмотр узлов на диске F. Уровень является allowlisted и не заменяет сырой архив доказательств.',
      'rule-label': 'Операционное правило:',
      'rule-text': 'Только внутри allowlist и канонической границы публикации. Никакой blanket migration. Никакой перезаписи ценных файлов на диске F.',
      'mosaic-note': 'Разрешённый локальный просмотр узлов на диске F. Уровень является allowlisted и не заменяет сырой архив доказательств.',
      'mosaic-rule': 'Операционное правило: здесь отображаются только разрешённые HTML-узлы диска F. Рабочий архив остаётся источником истины, а публичный репозиторий — безопасным слоем представления.'
    },
    ro: {
      'portal-title': 'PORTALUL PROBELOR ȘI ARHIVA MAESTRĂ',
      'portal-subtitle': 'Fixare criptografică și protecție a normelor Jus Cogens / Erga Omnes.',
      'nav-core': 'Nucleu arhivă',
      'nav-chronology': 'Cronologie',
      'nav-jus': 'Jus Cogens',
      'nav-theft': 'Dovada furtului',
      'nav-mosaic': 'Mozaic HTML',
      'evidence-nodes': 'NODURI DE PROBĂ',
      'navigation': 'NAVIGARE',
      'integrity': 'VERIFICARE INTEGRITATE',
      'site-status': 'Status: verificat ✓',
      'portal-foot': 'CASE-MACHERET-1997-2026 | Master Evidence Archive',
      'lang': 'Limbă',
      'mosaic-title': 'Mozaic HTML al probelor',
      'mosaic-subtitle': 'Vizualizare locală autorizată a nodurilor din discul F. Acest nivel este allowlisted și nu înlocuiește arhiva brută a probelor.',
      'rule-label': 'Regulă operațională:',
      'rule-text': 'Doar în cadrul allowlist-ului și a limitei canonice de publicare. Fără migrare în masă. Fără suprascrierea fișierelor valoroase de pe discul F.',
      'mosaic-note': 'Vizualizare locală autorizată a nodurilor din discul F. Acest nivel este allowlisted și nu înlocuiește arhiva brută a probelor.',
      'mosaic-rule': 'Regulă operațională: aici sunt afișate doar nodurile HTML autorizate de pe discul F. Arhiva de lucru rămâne sursa adevărului, iar depozitul public rămâne un strat sigur de prezentare.'
    },
    en: {
      'portal-title': 'EVIDENCE PORTAL & MASTER VAULT',
      'portal-subtitle': 'Cryptographic fixation and protection of Jus Cogens / Erga Omnes norms.',
      'nav-core': 'Core Vault',
      'nav-chronology': 'Chronology',
      'nav-jus': 'Jus Cogens',
      'nav-theft': 'Theft Evidence',
      'nav-mosaic': 'HTML Mosaic',
      'evidence-nodes': 'EVIDENCE NODES',
      'navigation': 'NAVIGATION',
      'integrity': 'INTEGRITY VERIFICATION',
      'site-status': 'Status: Verified ✓',
      'portal-foot': 'CASE-MACHERET-1997-2026 | Master Evidence Archive',
      'lang': 'Language',
      'mosaic-title': 'Evidence HTML Mosaic',
      'mosaic-subtitle': 'Authorized local view of the F-drive HTML nodes. This layer is allowlisted and does not replace the raw evidence archive.',
      'rule-label': 'Operational rule:',
      'rule-text': 'Only within the allowlist and canonical publication boundary. No blanket migration. No overwrite of value-bearing files on F drive.',
      'mosaic-note': 'Authorized local view of the F-drive HTML nodes. This layer is allowlisted and does not replace the raw evidence archive.',
      'mosaic-rule': 'Operational rule: only allowlisted F-drive HTML nodes are surfaced here. The working archive remains the source of truth, with the public repo kept as a safe presentation layer.'
    }
  };

  const defaultLang = localStorage.getItem('evidence-lang') || 'ru';

  function applyTranslation(lang) {
    const table = translations[lang] || translations.ru;
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach((node) => {
      const key = node.dataset.i18n;
      if (table[key]) {
        node.textContent = table[key];
      }
    });
    document.querySelectorAll('[data-i18n-value]').forEach((node) => {
      const key = node.dataset.i18nValue;
      if (table[key]) {
        node.value = table[key];
      }
    });
    const selectors = document.querySelectorAll('[data-lang-switch]');
    selectors.forEach((button) => {
      const active = button.dataset.langSwitch === lang;
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
      button.style.opacity = active ? '1' : '0.7';
    });
    localStorage.setItem('evidence-lang', lang);
  }

  document.addEventListener('DOMContentLoaded', function () {
    const switchers = document.querySelectorAll('[data-lang-switch]');
    switchers.forEach((button) => {
      button.addEventListener('click', function () {
        applyTranslation(button.dataset.langSwitch);
      });
    });
    applyTranslation(defaultLang);
  });
})();
