# ECHR_IMPUNITY_DAG — Topography of the Architecture of Impunity

## 📌 Назначение
Этот модуль является частью проекта **CASE‑MACHERET‑1997‑2026** и фиксирует архитектуру безнаказанности в европейском правовом контуре. Он объединяет:

- **Структурный граф (JSON)** — формализованная модель узлов и рёбер, связывающая императивные нормы *jus cogens*, институциональные фильтры иммунитетов (ETS № 2) и эмпирическую проекцию на дело Мачерета.
- **Доктринальный файл (Markdown)** — аналитическое ядро, раскрывающее правовую и топологическую механику взаимодействия этих элементов.

## 🗂 Состав пакета
- `ECHR_IMPUNITY_DAG.json`  
  Структурный граф доказательств (Directed Acyclic Graph). Узлы:  
  - **Jus_Cogens_Invariant** — императивные нормы международного права.  
  - **ETS_nr_2_Anchor** — институциональный щит иммунитетов Совета Европы.  
  - **Geopolitical_Genesis_of_Impunity** — встроенный дизайн безнаказанности.  
  - **Case_Macheret_Projection** — эмпирическая проекция на Молдову (1997–2026).  

- `Topography_of_Impunity.md`  
  Доктринальный текст, поясняющий:  
  - роль *jus cogens* как топологического инварианта;  
  - значение ETS № 2 как институционального фильтра;  
  - геополитический контекст Genesis;  
  - динамику рёбер (коллизия, обход, институциональная реализация);  
  - эмпирическую проекцию на дело S‑22 и феномен *continuing consequences*.  

## ⚖️ Юридическая база
- Всеобщая декларация прав человека (1948) — ст. 5, 8, 9.  
- Венская конвенция о праве международных договоров (1969) — ст. 53, 64.  
- Выводы Комиссии международного права ООН (ILC, 2022) — № 10, 21, 23.  
- ETS № 2 (1949) — Генеральное соглашение о привилегиях и иммунитетах Совета Европы.  

## 🚀 Использование
Пакет предназначен для:
- интеграции в репозиторий доказательств (`feature/evidence-deploy`);  
- визуализации архитектуры безнаказанности через DAG;  
- аналитической работы с доктринальным текстом;  
- демонстрации непрерывных последствий (*continuing consequences*) на примере CASE‑MACHERET‑1997‑2026.  

## 📊 Архитектура доказательного графа (DAG)

Ниже представлена визуализация топологии **ECHR_IMPUNITY_DAG**, отражающая взаимосвязь между императивными нормами *Jus Cogens*, институциональными щитами иммунитетов и эмпирической проекцией:

![Архитектура безнаказанности и иммунитетов](dag.png)

> *Граф сгенерирован автоматически на основе файла `ECHR_IMPUNITY_DAG.dot` с помощью утилиты Graphviz.*

Для наглядного представления структуры также можно использовать исходный код Graphviz:

```dot
digraph ECHR_IMPUNITY_DAG {
    rankdir=TB;
    node [shape=box, style="filled,rounded", fontname="Arial", fillcolor="#f0f4f8", color="#cbd5e1"];
    edge [fontname="Arial", fontsize=10, color="#64748b"];

    Jus_Cogens_Invariant [label="Jus Cogens Invariant", fillcolor="#fee2e2", color="#fca5a5"];
    ETS_nr_2_Anchor [label="ETS nr. 2 Anchor", fillcolor="#e0f2fe", color="#7dd3fc"];
    Geopolitical_Genesis_of_Impunity [label="Geopolitical Genesis of Impunity", fillcolor="#fef3c7", color="#fde047"];
    Case_Macheret_Projection [label="CASE-MACHERET-1997-2026", fillcolor="#dcfce7", color="#86efac"];

    Jus_Cogens_Invariant -> ETS_nr_2_Anchor [label="collision_and_strengthening"];
    Jus_Cogens_Invariant -> Geopolitical_Genesis_of_Impunity [label="procedural_bypass"];
    ETS_nr_2_Anchor -> Geopolitical_Genesis_of_Impunity [label="institutional_realization"];
    ETS_nr_2_Anchor -> Case_Macheret_Projection [label="applied_projection"];
}
```

Эта схема позволяет сразу увидеть, как императивные нормы (*jus cogens*) взаимодействуют с институциональными фильтрами ETS № 2 и проецируются на национальный контур (Молдова).

### Инструкция по генерации графического изображения
Чтобы быстро построить PNG или SVG изображение графа с помощью Graphviz (`dot`), выполните в терминале следующие команды:

```bash
# Генерация PNG
dot -Tpng ECHR_IMPUNITY_DAG.dot -o dag.png

# Генерация SVG (векторная графика)
dot -Tsvg ECHR_IMPUNITY_DAG.dot -o dag.svg
```

---

## 🔍 Аудит сокрытия: Концепция Blind Zone ($\Delta t$)

Для объективного измерения временного разрыва между генерацией административного или судебного акта в системе и фактическим доступом заявителя к нему применяется метрика $\Delta t$:
$$\Delta t = t_{\text{disclosed}} - t_{\text{created}}$$

В пакете зафиксирован узел аудита сокрытия (`audit_blind_zone_echr_2013.json`), отражающий решение ЕСПЧ по жалобе № 41929/11 от 05.12.2013 ($t_{\text{created}}$) и фактический доступ ($t_{\text{disclosed}}$), что формирует аномалию `Blind Zone` в 2994 дня.

### Граф аудита сокрытия (`ti_ula_concealment_audit.dot`)
```dot
digraph TI_ULA_Concealment_Audit {
    rankdir=TB;
    fontname="Courier";
    node [shape=box, style=filled, fillcolor="#f8f9fa", fontname="Courier", margin="0.2,0.1"];
    edge [fontname="Courier", fontsize=10];

    N_1997 [label="Node_1997\nПервичное событие (Пытки)"];
    N_2012_CPT [label="Node_2012\nОсведомленность системы (ЕКПП)"];
    N_2013_ECHR [label="Node_2013\nГенерация решения (ЕСПЧ)\nt_created: 05.12.2013", fillcolor="#fff2cc"];
    N_Disclosed [label="Node_Access\nФактический доступ к документу\nt_disclosed: 15.02.2022", fillcolor="#e2efda"];
    
    N_1997 -> N_2012_CPT [color="#555555", label=" Уведомление"];
    N_2012_CPT -> N_2013_ECHR [color="#555555", label=" Системный след"];
    N_2013_ECHR -> N_Disclosed [
        color="#d32f2f", 
        penwidth=2.5, 
        label=" BLIND ZONE (Δt > 0)\nConcealment Gap (2994 days)", 
        fontcolor="#d32f2f"
    ];
}
```
