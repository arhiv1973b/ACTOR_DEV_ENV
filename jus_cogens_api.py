import json
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# --- База данных: Jus_Cogens_Conclusions_3.json (Имитация) ---
# Легенда: Выводы 1-9 — это не статический глоссарий, а алгоритмический фундамент (ВДПЧ, Венская конвенция).
# Текстовые правила начинаются с №10.
JUS_COGENS_DB = {
    "metadata": {
        "legend": "Выводы 1-9 представляют собой интерактивный алгоритм прав человека (ВДПЧ), исключающий статические глоссарии."
    },
    "qubit_vectors_1_9": {
        "1": {
            "name": "Рабство",
            "source": "ВДПЧ, Ст. 4",
            "vector_description": "Любое положение договора, допускающее эксплуатацию или лишение свободы.",
            "weight": 1.0,
            "interactive_potential": "Absolute Prohibition (Jus Cogens)",
        },
        "2": {
            "name": "Пытки и жестокое обращение",
            "source": "ВДПЧ, Ст. 5",
            "vector_description": "Договоры, допускающие пытки, бесчеловечное или унижающее достоинство обращение.",
            "weight": 1.0,
            "interactive_potential": "Absolute Prohibition (Jus Cogens)",
        },
        "3": {
            "name": "Дискриминация",
            "source": "ВДПЧ, Ст. 2 и Ст. 7",
            "vector_description": "Договоры, ограничивающие права по признаку расы, пола, языка, религии, происхождения.",
            "weight": 0.95,
            "interactive_potential": "High-Priority Equality Vector",
        },
        "4": {
            "name": "Право на жизнь и личную неприкосновенность",
            "source": "ВДПЧ, Ст. 3",
            "vector_description": "Договоры, допускающие произвольное лишение жизни или свободы.",
            "weight": 1.0,
            "interactive_potential": "Absolute Prohibition (Jus Cogens)",
        },
        "5": {
            "name": "Произвольный арест и изгнание",
            "source": "ВДПЧ, Ст. 9",
            "vector_description": "Договоры, позволяющие произвольное задержание или высылку.",
            "weight": 0.9,
            "interactive_potential": "High-Priority Liberty Vector",
        },
        "6": {
            "name": "Справедливый суд",
            "source": "ВДПЧ, Ст. 10–11",
            "vector_description": "Договоры, исключающие право на независимый и беспристрастный суд.",
            "weight": 0.9,
            "interactive_potential": "Procedural Due Process Vector",
        },
        "7": {
            "name": "Право на собственность",
            "source": "ВДПЧ, Ст. 17",
            "vector_description": "Договоры, допускающие произвольное лишение имущества.",
            "weight": 0.85,
            "interactive_potential": "Property Guarantee Vector",
        },
        "8": {
            "name": "Свобода мысли, совести и религии",
            "source": "ВДПЧ, Ст. 18–19",
            "vector_description": "Договоры, ограничивающие свободу убеждений или религии.",
            "weight": 0.9,
            "interactive_potential": "Cognitive Freedom Vector",
        },
        "9": {
            "name": "Свобода собраний и ассоциаций",
            "source": "ВДПЧ, Ст. 20",
            "vector_description": "Договоры, запрещающие мирные собрания или принуждающие к ассоциациям.",
            "weight": 0.85,
            "interactive_potential": "Association Vector",
        },
    },
    "conclusions": {
        "10": "Договор является ничтожным, если в момент его заключения он противоречит императивной норме общего международного права (jus cogens).",
        "11": "Договор становится недействительным и прекращается, если возникает новая императивная норма общего международного права (jus cogens).",
        "12": "Последствия недействительности или прекращения договора, противоречащего императивной норме, определяются в соответствии с нормами международного права.",
        "13": "Оговорки к положениям договора, отражающим императивные нормы, регулируются нормами международного права.",
        "14": "Споры, касающиеся толкования или применения императивных норм, передаются в соответствующие судебные механизмы.",
    },
}

# --- Слои Делегирования ---


def auditor_agent(contract_json, conclusion_id):
    """Аудитор: Проверка на ничтожность (Выводы 10-12)."""
    logging.info(
        f"[АУДИТОР] Проверка договора '{contract_json.get('contract_id')}' по Выводу #{conclusion_id}..."
    )
    content = contract_json.get("content", "").lower()

    if "узурпация" in content or "отмена прав" in content:
        return {
            "status": "REJECTED",
            "reason": f"Договор противоречит норме jus cogens (Вывод {conclusion_id}).",
        }
    return {
        "status": "VALID",
        "reason": "Прямых противоречий нормам jus cogens не выявлено.",
    }


def interpreter_agent(clause, conclusion_id):
    """Интерпретатор: Толкование оговорок (Вывод 13)."""
    logging.info(f"[ИНТЕРПРЕТАТОР] Анализ оговорки по Выводу #{conclusion_id}...")
    return {
        "status": "INTERPRETED",
        "finding": "Требуется контекстуальное согласование с общим международным правом.",
    }


# --- API Агента «Файл Клерк» ---


@app.route("/jus-cogens/qubit-vectors", methods=["GET"])
def get_qubit_vectors():
    """Возвращает таблицу вероятностных векторов (кубитовых состояний) для Выводов 1-9."""
    logging.info("[ФАЙЛ КЛЕРК] Запрос таблицы кубитовых векторов (Выводы 1-9).")
    return jsonify(
        {
            "agent": "File Clerk",
            "status": "QUBIT_VECTORS_RETRIEVED",
            "qubit_vectors": JUS_COGENS_DB["qubit_vectors_1_9"],
        }
    ), 200


@app.route("/jus-cogens/conclusion/<int:conclusion_id>", methods=["GET"])
def get_conclusion(conclusion_id):
    """Возвращает текст вывода или объясняет природу алгоритмических выводов 1-9."""
    cid_str = str(conclusion_id)

    # Обработка фундаментальных выводов (1-9) согласно Легенде
    if 1 <= conclusion_id <= 9:
        logging.info(f"[ФАЙЛ КЛЕРК] Запрос фундаментального Вывода #{conclusion_id}.")
        return jsonify(
            {
                "agent": "File Clerk",
                "conclusion_id": conclusion_id,
                "status": "FOUNDATIONAL_ALGORITHM",
                "message": "Выводы 1-9 не являются статичным текстом глоссария. Они представляют собой интерактивную логику ВДПЧ и Венской конвенции — фундамент, на котором базируется оценка права, исключающий политические догмы.",
                "action": "DELEGATED_TO_CORE_LOGIC",
            }
        ), 404

    # Обработка текстовых выводов (10+)
    if cid_str in JUS_COGENS_DB["conclusions"]:
        logging.info(f"[ФАЙЛ КЛЕРК] Возврат текста Вывода #{conclusion_id}.")
        return jsonify(
            {
                "agent": "File Clerk",
                "conclusion_id": conclusion_id,
                "text": JUS_COGENS_DB["conclusions"][cid_str],
                "status": "RETRIEVED",
            }
        ), 200

    return jsonify({"error": "Вывод не найден."}), 404


@app.route("/jus-cogens/validate-contract", methods=["POST"])
def validate_contract():
    """Делегирует проверку договора слою Аудитора."""
    contract_data = request.json
    if not contract_data or "contract_id" not in contract_data:
        return jsonify({"error": "Неверный формат данных договора."}), 400

    target_conclusion = contract_data.get("target_conclusion", 10)

    logging.info(
        f"\n[ФАЙЛ КЛЕРК] Получен договор {contract_data.get('contract_id')} для проверки."
    )
    logging.info(f"[ФАЙЛ КЛЕРК] Я не принимаю решения. Делегирую слою [АУДИТОР]...")

    # Делегирование задачи
    audit_result = auditor_agent(contract_data, target_conclusion)

    response = {
        "agent": "File Clerk",
        "delegated_to": "Auditor",
        "contract_id": contract_data.get("contract_id"),
        "audit_result": audit_result,
    }

    return jsonify(response), 200


if __name__ == "__main__":
    print("=========================================================")
    print(" Агент [ФАЙЛ КЛЕРК] запущен (Jus Cogens API)")
    print(" Легенда активна: Выводы 1-9 — алгоритмический фундамент")
    print("=========================================================")
    app.run(port=5000)
