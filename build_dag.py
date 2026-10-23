import os
import json
import glob
from datetime import datetime

def calculate_unique_concealment_span(intervals):
    """
    Объединяет пересекающиеся интервалы (t_created, t_disclosed) 
    и рассчитывает общую уникальную продолжительность сокрытия в днях.
    """
    if not intervals:
        return 0
    
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    for current_start, current_end in sorted_intervals:
        if not merged:
            merged.append([current_start, current_end])
        else:
            prev_start, prev_end = merged[-1]
            if current_start <= prev_end:
                merged[-1][1] = max(prev_end, current_end)
            else:
                merged.append([current_start, current_end])
                
    total_days = sum((end - start).days for start, end in merged)
    return total_days

def build_concealment_dag():
    doctrine_dir = r"H:\ACTOR_DEV_ENV\🏛️_EVIDENCE\LEGAL_DOCTRINE"
    json_files = glob.glob(os.path.join(doctrine_dir, "*.json"))
    
    nodes = []
    edges = []
    intervals = []
    
    # Добавляем корневые узлы
    nodes.append(('N_1997', 'Базовый узел (1997)\\nФакт пыток (Jus Cogens)', '#f8f9fa'))
    nodes.append(('N_2021', 'Точка раскрытия\\n(Факт обнаружения)', '#e2efda'))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if data.get('node_type') in ['critical_concealment_anomaly', 'concealment_audit']:
                    node_id = data.get('node_id') or os.path.basename(file_path).replace('.json', '')
                    node_id_clean = node_id.replace('-', '_').replace('.', '_')
                    
                    temp_metrics = data.get('temporal_metrics', {})
                    t_created_str = temp_metrics.get('t_created', 'Unknown')
                    t_disclosed_str = temp_metrics.get('t_disclosed', 'Unknown')
                    t_created = t_created_str[:10]
                    gap = temp_metrics.get('concealment_gap_days', 0)
                    
                    # Извлекаем правовые последствия (legal_consequence)
                    legal = data.get('legal_consequence', {})
                    continuing_offense = legal.get('continuing_offense', False)
                    status = legal.get('status', '')
                    nullity_basis = legal.get('nullity_basis', '')
                    
                    # Собираем интервалы для расчета уникальной дельты
                    if t_created_str != 'Unknown' and t_disclosed_str != 'Unknown':
                        try:
                            dt_start = datetime.fromisoformat(t_created_str.replace('Z', '+00:00'))
                            dt_end = datetime.fromisoformat(t_disclosed_str.replace('Z', '+00:00'))
                            intervals.append((dt_start, dt_end))
                        except Exception:
                            pass
                    
                    # Формируем расширенную метку узла с юридическим статусом
                    label = f"{node_id}\\nt_created: {t_created}\\nGap: {gap}d"
                    if continuing_offense:
                        label += "\\n[CONTINUING OFFENSE]"
                    if status:
                        label += f"\\nStatus: {status}"
                    
                    nodes.append((node_id_clean, label, '#fff2cc'))
                    
                    # Формируем метку для красной дуги Blind Zone с правовым обоснованием
                    edge_label = f"BLIND ZONE: {gap} days"
                    if continuing_offense:
                        edge_label += "\\n[Jus Cogens Violation]"
                    if nullity_basis:
                        short_basis = nullity_basis.split('-')[0].strip()
                        edge_label += f"\\nBasis: {short_basis}"
                        
                    edges.append((node_id_clean, 'N_2021', edge_label, '#d32f2f'))
                    
                    # Обработка родительских указателей (parent_node_hash)
                    parent = data.get('dag_pointers', {}).get('parent_node_hash')
                    if parent:
                        edges.append(('N_1997', node_id_clean, 'chain', '#555555'))
                elif data.get('node_type') == 'evidence_anchor':
                    node_id = data.get('node_id') or os.path.basename(file_path).replace('.json', '')
                    node_id_clean = node_id.replace('-', '_').replace('.', '_')
                    label = f"{node_id}\\nEvidence Anchor\\nCase: 1-568/98\\nApostilles: 2021\\n[Actus Nullus / VCLT 71(1a)]"
                    nodes.append((node_id_clean, label, '#ffe6cc'))
                    edges.append(('N_1997', node_id_clean, 'root anchor', '#d32f2f'))
                    edges.append((node_id_clean, 'N_2021', 'continuing consequences', '#d32f2f'))
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    # Расчет уникального кумулятивного интервала
    unique_gap_days = calculate_unique_concealment_span(intervals)
    unique_gap_years = round(unique_gap_days / 365.25, 2)

    # Генерация содержимого DOT-файла
    dot_content = "digraph TI_ULA_Concealment_AutoGenerated {\n"
    dot_content += "    rankdir=TB;\n"
    dot_content += "    fontname=\"Courier\";\n"
    dot_content += f'    labelloc="t";\n'
    dot_content += f'    label="TI-ULA CONCEALMENT AUDIT\\nUnique Cumulative Gap: {unique_gap_days} days (~{unique_gap_years} years) | Nullity: A_sub ≡ 0";\n'
    dot_content += "    node [shape=box, style=filled, fillcolor=\"#f8f9fa\", fontname=\"Courier\", margin=\"0.2,0.1\"];\n"
    dot_content += "    edge [fontname=\"Courier\", fontsize=9];\n\n"
    
    for n_id, label, color in set(nodes):
        dot_content += f'    {n_id} [label="{label}", fillcolor="{color}"];\n'
        
    dot_content += "\n"
    for src, dst, label, color in set(edges):
        if color == '#d32f2f':
            dot_content += f'    {src} -> {dst} [color="{color}", penwidth=2.5, label=" {label}", fontcolor="{color}"];\n'
        else:
            dot_content += f'    {src} -> {dst} [color="{color}", label=" {label}"];\n'
            
    dot_content += "}\n"
    
    output_dot = os.path.join(doctrine_dir, "auto_generated_concealment.dot")
    with open(output_dot, 'w', encoding='utf-8') as f:
        f.write(dot_content)
        
    print(f"Successfully generated Legal-Proof DAG DOT file at: {output_dot}")
    print(f"Unique Cumulative Concealment Span: {unique_gap_days} days (~{unique_gap_years} years)")

if __name__ == '__main__':
    build_concealment_dag()
