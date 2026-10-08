# file_clerk_agent.py
import os
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Load Jus Cogens conclusions (10-23)
jus_cogens_path = "evidence/Jus_Cogens_Conclusions_3.json"
if os.path.exists(jus_cogens_path):
    with open(jus_cogens_path, "r", encoding="utf-8") as f:
        conclusions_data = json.load(f)
        conclusions = {
            str(c.get("номер", i)): c
            for i, c in enumerate(conclusions_data.get("Выводы", []), start=10)
        }
else:
    conclusions = {}

# Legal instruments integration: UDHR 1948 and VCLT 1969
INTERNATIONAL_INSTRUMENTS = {
    "VCLT_1969": {
        "name": "Vienna Convention on the Law of Treaties (1969)",
        "key_articles": {
            "53": "Treaties conflicting with a peremptory norm of general international law (jus cogens) are void.",
            "64": "Emergence of a new peremptory norm of general international law (jus cogens): any existing treaty which is in conflict with that norm becomes void and terminates.",
        },
    },
    "UDHR_1948": {
        "name": "Universal Declaration of Human Rights (1948)",
        "key_articles": {
            "5": "No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment.",
            "9": "No one shall be subjected to arbitrary arrest, detention or exile.",
            "12": "No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence.",
        },
    },
}


def auditor_check(contract_text):
    text_lower = contract_text.lower()
    violations = []

    # Check against Jus Cogens core prohibitions
    if "рабство" in text_lower or "slavery" in text_lower:
        violations.append(
            "Prohibition of slavery (Violates Jus Cogens & UDHR Article 4)"
        )
    if "пытки" in text_lower or "torture" in text_lower:
        violations.append(
            "Prohibition of torture (Violates Jus Cogens & UDHR Article 5)"
        )
    if "произвольный арест" in text_lower or "arbitrary detention" in text_lower:
        violations.append(
            "Prohibition of arbitrary detention (Violates UDHR Article 9)"
        )

    # Check against VCLT 1969 Art 53/64 if treaty/contract conflict is detected
    if violations:
        return {
            "status": "VOID",
            "legal_basis": ["VCLT 1969 Article 53", "Jus Cogens peremptory norms"],
            "violations": violations,
            "reason": "Contract/document conflicts with peremptory norms of international law (jus cogens) and is null and void.",
        }

    return {
        "status": "VALID",
        "legal_basis": ["VCLT 1969", "UDHR 1948", "Jus Cogens"],
        "reason": "No explicit violation of jus cogens or international human rights instruments detected in text.",
    }


@app.route("/jus-cogens/conclusion/<num>", methods=["GET"])
def get_conclusion(num):
    if num in conclusions:
        return jsonify(conclusions[num])
    return jsonify({"error": "Conclusion not found", "available_range": "10-23"}), 404


@app.route("/international-instruments", methods=["GET"])
def get_instruments():
    return jsonify(INTERNATIONAL_INSTRUMENTS)


@app.route("/jus-cogens/validate-contract", methods=["POST"])
def validate_contract():
    data = request.get_json() or {}
    contract_id = data.get("contract_id", "DOC-UNKNOWN")
    content = data.get("content", "")
    result = auditor_check(content)
    return jsonify(
        {
            "contract_id": contract_id,
            "validation": result,
            "frameworks_checked": ["Jus Cogens", "VCLT 1969", "UDHR 1948"],
        }
    )


if __name__ == "__main__":
    app.run(port=5000)
