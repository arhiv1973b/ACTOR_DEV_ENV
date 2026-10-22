#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDPR & Local Data Compliance Forensic Audit Tool
Designed for air-gapped forensic pipelines to verify cookie and storage artifacts.
Computes SHA-256 hashes and generates structured JSON audit reports.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime

# Определение категорий и критериев строгого соответствия GDPR
ESSENTIAL_PROVIDERS = {"CloudFlare Inc", "Cloudflare", "Social V1 API", "Google", "HAProxy", "Osano"}
REQUIRED_ESSENTIAL_COOKIES = {"osano_consentmanager", "osano_consentmanager_uuid"}

def calculate_sha256(file_path):
    """Вычисляет SHA-256 хэш файла для обеспечения криминалистической целостности."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"[!] Ошибка чтения файла для хэширования: {e}", file=sys.stderr)
        sys.exit(1)

def parse_artifacts_text(text_content):
    """
    Парсит текстовый дамп панели согласия (формат, переданный в исходном запросе).
    Возвращает структурированный список элементов хранения.
    """
    items = []
    current_category = "Unknown"
    current_item = {}
    
    lines = text_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Определяем категории
        if "Основные or Минимально необходимые" in line or "Основные" in line:
            current_category = "Essential"
            i += 1
            continue
        elif "Таргетированная реклама" in line:
            current_category = "Targeted Advertising"
            i += 1
            continue
        elif "Персонализация" in line:
            current_category = "Personalization"
            i += 1
            continue
        elif "Аналитика" in line:
            current_category = "Analytics"
            i += 1
            continue

        # Парсинг полей элемента
        if line == "имя" and i + 1 < len(lines):
            if current_item and "name" in current_item:
                items.append(current_item)
                current_item = {"category": current_category}
            elif not current_item:
                current_item = {"category": current_category}
            
            current_item["name"] = lines[i+1].strip()
            i += 2
            continue
        elif line == "поставщик" and i + 1 < len(lines):
            current_item["provider"] = lines[i+1].strip()
            i += 2
            continue
        elif line == "Тип" and i + 1 < len(lines):
            current_item["type"] = lines[i+1].strip()
            i += 2
            continue
        elif line == "истечение" and i + 1 < len(lines):
            current_item["expiration"] = lines[i+1].strip()
            i += 2
            continue
        elif line == "Цель" and i + 1 < len(lines):
            goal_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() not in ["имя", "поставщик", "Тип", "истечение", "Цель"] and not any(cat in lines[i] for cat in ["Основные", "Таргетированная", "Персонализация", "Аналитика"]):
                goal_lines.append(lines[i].strip())
                i += 1
            current_item["purpose"] = " ".join(goal_lines)
            continue
        
        i += 1

    if current_item and "name" in current_item:
        items.append(current_item)

    return items

def perform_gdpr_audit(items):
    """Выполняет аудит собранных артефактов на предмет соблюдения GDPR и регламентов."""
    violations = []
    warnings = []
    audit_results = {
        "total_items": len(items),
        "categories_breakdown": {},
        "compliance_status": "PASS"
    }

    consent_manager_found = False

    for item in items:
        if not isinstance(item, dict):
            continue
        cat = item.get("category", "Unknown")
        audit_results["categories_breakdown"][cat] = audit_results["categories_breakdown"].get(cat, 0) + 1
        
        name = item.get("name", "")
        provider = item.get("provider", "Поставщик не указан")
        
        if name in REQUIRED_ESSENTIAL_COOKIES:
            consent_manager_found = True

        if provider == "Поставщик не указан" and cat in ["Targeted Advertising", "Analytics"]:
            warnings.append(f"Алерт: Трекер '{name}' в категории '{cat}' не имеет указанного поставщика.")

        if cat == "Targeted Advertising" and provider in ESSENTIAL_PROVIDERS:
            violations.append(f"Нарушение логики: Рекламный трекер '{name}' классифицирован под доверенным провайдером '{provider}'.")

    if not consent_manager_found:
        violations.append("Критическое нарушение: Не найдены обязательные артефакты согласия (Osano Consent Manager).")

    if violations:
        audit_results["compliance_status"] = "FAIL"
    elif warnings:
        audit_results["compliance_status"] = "WARNING"

    audit_results["violations"] = violations
    audit_results["warnings"] = warnings
    return audit_results

def main():
    parser = argparse.ArgumentParser(
        description="GDPR & Local Data Compliance Forensic Audit CLI Tool"
    )
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Путь к входному файлу со списком артефактов (txt или json)"
    )
    parser.add_argument(
        "-o", "--output", 
        default="gdpr_forensic_audit_report.json", 
        help="Путь для сохранения итогового JSON-отчета"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[!] Ошибка: Входной файл '{args.input}' не найден.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Запуск криминалистического аудита для файла: {args.input}")
    
    input_sha256 = calculate_sha256(args.input)
    print(f"[+] SHA-256 входного артефакта: {input_sha256}")

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    if args.input.endswith(".json"):
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "messages" in data:
                full_text = "\n".join([msg.get("content", "") for msg in data["messages"]])
                items = parse_artifacts_text(full_text)
            elif isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "parsed_items" in data:
                items = data["parsed_items"]
            else:
                items = parse_artifacts_text(content)
        except json.JSONDecodeError:
            items = parse_artifacts_text(content)
    else:
        items = parse_artifacts_text(content)

    audit_data = perform_gdpr_audit(items)

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_file": args.input,
        "input_sha256": input_sha256,
        "audit_summary": audit_data,
        "parsed_items": items
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    output_sha256 = calculate_sha256(args.output)
    
    print(f"[+] Аудит завершен. Статус: {audit_data['compliance_status']}")
    print(f"[+] Отчет сохранен в: {args.output}")
    print(f"[+] SHA-256 отчета: {output_sha256}")

    if audit_data['compliance_status'] == "FAIL":
        sys.exit(2)
    elif audit_data['compliance_status'] == "WARNING":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
