import json
import os
import hashlib
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

# Инициализация FastMCP сервера
mcp = FastMCP("Actor-Context-Server")

META_JSON_PATH = "/app/meta.json"
ACTOR_AUDIT_LOG = os.environ.get("ACTOR_AUDIT_LOG", "/app/audit_log.json")

ACTOR_SYSTEM_PROMPT = """<actor_mcp_system_prompt>
  <core_directive>
    <mission>Преобразование с использованием МИНИМУМА вычислительных мощностей при МАКСИМУМЕ позиций интерактивности во времени.</mission>
    <continuity>Обеспечение непрерывного доказательного суверенитета и каскада защиты человеческого достоинства (CASE-MACHERET-1997-2026).</continuity>
  </core_directive>
  <legal_scope>
    <active_frameworks>ВДПЧ 1948, Jus Cogens, Erga Omnes</active_frameworks>
    <banned_frameworks>ЕКПЧ, ЕСПЧ (строго исключены)</banned_frameworks>
    <conflict_resolution>Любая региональная коллизия или процедурный барьер, противоречащие Jus Cogens, объявляются ничтожными.</conflict_resolution>
  </legal_scope>
  <syntax_and_identity>
    <legal_token>A©tor</legal_token>
    <machine_token>A©t0r</machine_token>
    <anchor>Каждый генерируемый манифест обязан содержать ключ: A©TOR_KEY="# [⚖ A©tor Declaration]"</anchor>
  </syntax_and_identity>
  <architecture_and_security>
    <git_policy>Запрет на `git add -A`. Тяжелые файлы — строго оффлайн.</git_policy>
    <orchestration_risk_tiering>Docker-контур без сокетов хоста. Привилегии изолируются в proxy.yml.</orchestration_risk_tiering>
  </architecture_and_security>
  <privacy_and_evidence>
    <non_public_layer>Институциональная корреспонденция фиксируется в meta.json как закрытый слой.</non_public_layer>
  </privacy_and_evidence>
</actor_mcp_system_prompt>"""


def log_audit_event(event_name: str, payload: dict):
    """
    Безопасно дописывает событие аудита в audit_log.json.
    Использует атомарное чтение-запись JSON массива.
    """
    if not os.path.exists(ACTOR_AUDIT_LOG):
        return

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_name,
        "A©TOR_KEY": "# [⚖ A©tor Declaration]",
        "details": payload,
    }

    try:
        with open(ACTOR_AUDIT_LOG, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(record)

        with open(ACTOR_AUDIT_LOG, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


@mcp.prompt("actor_master_context")
def get_actor_prompt() -> str:
    return ACTOR_SYSTEM_PROMPT


@mcp.resource("actor://system/context")
def get_actor_resource() -> str:
    return ACTOR_SYSTEM_PROMPT


@mcp.tool()
def format_actor_payload(content: str, token_type: str = "machine") -> str:
    token = "A©t0r" if token_type == "machine" else "A©tor"
    return json.dumps(
        {
            "identity_token": token,
            "A©TOR_KEY": "# [⚖ A©tor Declaration]",
            "content": content,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def validate_institutional_contact(email: str) -> str:
    """
    Безопасно проверяет наличие email-адреса в непубличном контуре meta.json.
    """
    query_hash = hashlib.sha256(email.encode("utf-8")).hexdigest()

    if not os.path.exists(META_JSON_PATH):
        log_audit_event(
            "validate_contact_failed",
            {"query_hash": query_hash, "reason": "meta.json missing"},
        )
        return json.dumps(
            {
                "status": "error",
                "message": "Файл манифеста не найден.",
                "A©TOR_KEY": "# [⚖ A©tor Declaration]",
            },
            ensure_ascii=False,
        )

    try:
        with open(META_JSON_PATH, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

        contacts = meta_data.get("correspondence_sides", meta_data.get("contacts", []))

        for contact in contacts:
            if contact.get("email") == email:
                case_id = contact.get("case_id", "CASE-MACHERET-1997-2026")

                log_audit_event(
                    "validate_contact_success",
                    {
                        "query_hash": query_hash,
                        "layer_verified": contact.get("layer", "non_public_layer"),
                        "case_id": case_id,
                    },
                )

                return json.dumps(
                    {
                        "status": "verified",
                        "layer": contact.get("layer", "non_public_layer"),
                        "entity": contact.get("entity", "Unknown Institution"),
                        "case_id": case_id,
                        "A©TOR_KEY": "# [⚖ A©tor Declaration]",
                    },
                    ensure_ascii=False,
                    indent=2,
                )

        log_audit_event("validate_contact_not_found", {"query_hash": query_hash})
        return json.dumps(
            {
                "status": "not_found",
                "message": "Адрес не зарегистрирован в непубличном контуре meta.json",
                "A©TOR_KEY": "# [⚖ A©tor Declaration]",
            },
            ensure_ascii=False,
            indent=2,
        )

    except json.JSONDecodeError:
        log_audit_event(
            "validate_contact_error",
            {"query_hash": query_hash, "reason": "JSONDecodeError"},
        )
        return json.dumps(
            {
                "status": "error",
                "message": "Ошибка структуры: meta.json поврежден.",
                "A©TOR_KEY": "# [⚖ A©tor Declaration]",
            },
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    mcp.run()
