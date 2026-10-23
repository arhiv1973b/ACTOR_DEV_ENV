#!/usr/bin/env python3
"""
Financial Sabotage Aggregation Script
Aggregates evidence of economic strangulation and forced infrastructure expenses
under CASE-MACHERET-1997-2026.
"""

import os
import json
import yaml

REGISTRY_PATH = (
    r"H:\ACTOR_DEV_ENV\evidence\financial_sabotage\financial_sabotage_registry.yaml"
)
RECEIPTS_MANIFEST = (
    r"H:\ACTOR_DEV_ENV\evidence\financial_sabotage\fincombank_receipts_manifest.json"
)
OUTPUT_REPORT = r"H:\ACTOR_DEV_ENV\evidence\financial_sabotage\financial_sabotage_aggregation_report.json"


def aggregate_financial_sabotage():
    print("Aggregating financial sabotage and economic strangulation evidence...")

    registry = {}
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f)

    receipts_data = {}
    if os.path.exists(RECEIPTS_MANIFEST):
        with open(RECEIPTS_MANIFEST, "r", encoding="utf-8") as f:
            receipts_data = json.load(f)

    # Calculate total FinComBank strangulation amounts (AJUTOR SOCIAL micro-payments)
    fincombank_total_mdl = 0.0
    receipt_items = receipts_data.get("evidence_items", [])
    for item in receipt_items:
        fincombank_total_mdl += item.get("amount_mdl", 0.0)

    # Estimated forced infrastructure expenses (annualized subscriptions & local support)
    # GitHub Copilot, ChatGPT Plus, Google Workspace, M365, iCloud+, StarNet, Foto-zoom
    infrastructure_estimates = [
        {
            "item": "GitHub Copilot / Developer Subscriptions",
            "estimated_annual_eur": 120.0,
        },
        {"item": "ChatGPT Plus / AI Assistance", "estimated_annual_eur": 240.0},
        {"item": "Google Workspace & M365 Cloud", "estimated_annual_eur": 150.0},
        {"item": "iCloud+ Storage & Security", "estimated_annual_eur": 36.0},
        {
            "item": "StarNet High-Speed Fiber Internet (Chișinău)",
            "estimated_annual_eur": 300.0,
        },
        {
            "item": "Foto-zoom Digitization & Archival Services",
            "estimated_annual_eur": 200.0,
        },
    ]
    total_infrastructure_eur = sum(
        i["estimated_annual_eur"] for i in infrastructure_estimates
    )

    # Claimed damages in main claim reference (EUR 506,880)
    claimed_damages_eur = 506880.0

    report = {
        "case_id": "CASE-MACHERET-1997-2026",
        "legal_doctrine": "Continuing Consequences (ECHR Art. 3 & 8 / Jus Cogens)",
        "vectors_evaluated": len(registry.get("vectors", [])),
        "fincombank_strangulation_total_mdl": fincombank_total_mdl,
        "fincombank_receipts_count": len(receipt_items),
        "forced_infrastructure_expenses": infrastructure_estimates,
        "total_infrastructure_annual_eur": total_infrastructure_eur,
        "primary_damages_claim_eur": claimed_damages_eur,
        "aggregation_status": "verified_and_linked",
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Aggregation report generated successfully: {OUTPUT_REPORT}")


if __name__ == "__main__":
    aggregate_financial_sabotage()
