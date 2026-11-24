import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _normalize_issuer(issuer: Any) -> Any:
    """Приводит issuer к каноническому виду для устойчивого сравнения."""
    if isinstance(issuer, dict):
        return {str(k): str(v) for k, v in sorted(issuer.items())}
    if isinstance(issuer, (list, tuple)):
        return str(issuer)
    return issuer


def _field_diff(prev_val: Any, curr_val: Any) -> dict[str, Any]:
    changed = prev_val is not None and curr_val is not None and prev_val != curr_val
    return {
        "changed": changed,
        "previous": prev_val,
        "current": curr_val,
    }


def compare_and_update_state(
    current_tls: dict[str, Any],
    state_path: Path,
    update_file: bool = True,
) -> dict[str, Any]:
    """Сравнивает SHA-256, notBefore, notAfter и issuer сертификата/цепочки."""
    peer = current_tls.get("peer_cert") or current_tls.get("peer_cert_unverified") or {}

    curr_cert_sha256 = peer.get("sha256_der")
    curr_chain_sha256 = current_tls.get("chain_sha256")  # опционально: list[str]
    curr_not_before = peer.get("notBefore")
    curr_not_after = peer.get("notAfter")
    curr_issuer = _normalize_issuer(peer.get("issuer"))
    checked_at = (
        current_tls.get("checked_at_utc") or datetime.now(timezone.utc).isoformat()
    )

    prev_state: dict[str, Any] = {}
    if state_path.exists():
        prev_state = json.loads(state_path.read_text(encoding="utf-8"))

    prev_cert_sha256 = prev_state.get("peer_cert_sha256")
    prev_chain_sha256 = prev_state.get("chain_sha256")
    prev_not_before = prev_state.get("notBefore")
    prev_not_after = prev_state.get("notAfter")
    prev_issuer = _normalize_issuer(prev_state.get("issuer"))

    cert_diff = _field_diff(prev_cert_sha256, curr_cert_sha256)
    chain_diff = _field_diff(prev_chain_sha256, curr_chain_sha256)
    not_before_diff = _field_diff(prev_not_before, curr_not_before)
    not_after_diff = _field_diff(prev_not_after, curr_not_after)
    issuer_diff = _field_diff(prev_issuer, curr_issuer)

    is_initial_baseline = prev_cert_sha256 is None and curr_cert_sha256 is not None
    any_changed = any(
        d["changed"]
        for d in (cert_diff, chain_diff, not_before_diff, not_after_diff, issuer_diff)
    )

    comparison = {
        "host": current_tls.get("host", "apostila.gov.md"),
        "checked_at_utc": checked_at,
        "initial_baseline": is_initial_baseline,
        "any_changed": any_changed,
        "cert_sha256": cert_diff,
        "chain_sha256": chain_diff,
        "notBefore": not_before_diff,
        "notAfter": not_after_diff,
        "issuer": issuer_diff,
    }

    if update_file and curr_cert_sha256:
        new_state = {
            "host": comparison["host"],
            "peer_cert_sha256": curr_cert_sha256,
            "chain_sha256": curr_chain_sha256,
            "notBefore": curr_not_before,
            "notAfter": curr_not_after,
            "issuer": curr_issuer,
            "last_seen_utc": checked_at,
            "last_changed_utc": (
                checked_at
                if (any_changed or is_initial_baseline)
                else prev_state.get("last_changed_utc")
            ),
        }
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(new_state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return comparison
