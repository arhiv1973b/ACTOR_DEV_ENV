import hashlib
import json
import socket
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _cert_name_to_dict(rdn_tuple: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    if not rdn_tuple:
        return result
    for part in rdn_tuple:
        for k, v in part:
            result[str(k)] = str(v)
    return result


def inspect_tls_chain(
    host: str, port: int = 443, timeout: float = 10.0
) -> dict[str, Any]:
    """Снимает сведения о TLS-сессии и цепочке сертификатов для узла."""
    info: dict[str, Any] = {
        "host": host,
        "port": port,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "strict_verify_ok": False,
        "strict_verify_error": None,
        "protocol": None,
        "cipher": None,
        "peer_cert": None,
        "chain_note": "Python ssl exposes peer cert and verification error; use openssl s_client for full intermediate PEM chain if needed.",
    }

    # 1. Проверка со строгой валидацией (как делает клиент при проверке доверия)
    strict_ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with strict_ctx.wrap_socket(sock, server_hostname=host) as tls_sock:
                info["strict_verify_ok"] = True
                info["protocol"] = tls_sock.version()
                info["cipher"] = tls_sock.cipher()
                cert = tls_sock.getpeercert(binary_form=False)
                der = tls_sock.getpeercert(binary_form=True)
                info["peer_cert"] = {
                    "subject": _cert_name_to_dict(cert.get("subject")) if cert else {},
                    "issuer": _cert_name_to_dict(cert.get("issuer")) if cert else {},
                    "notBefore": cert.get("notBefore") if cert else None,
                    "notAfter": cert.get("notAfter") if cert else None,
                    "serialNumber": cert.get("serialNumber") if cert else None,
                    "sha256_der": hashlib.sha256(der).hexdigest() if der else None,
                }
        return info
    except ssl.SSLCertVerificationError as exc:
        info["strict_verify_error"] = {
            "type": "SSLCertVerificationError",
            "verify_code": exc.verify_code,
            "verify_message": exc.verify_message,
            "reason": str(exc),
        }
    except Exception as exc:
        info["strict_verify_error"] = {
            "type": type(exc).__name__,
            "reason": str(exc),
        }

    # 2. Снятие серверного сертификата без валидации доверия для диагностики дефекта цепочки
    unverified_ctx = ssl.create_default_context()
    unverified_ctx.check_hostname = False
    unverified_ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with unverified_ctx.wrap_socket(sock, server_hostname=host) as tls_sock:
                info["protocol"] = tls_sock.version()
                info["cipher"] = tls_sock.cipher()
                der = tls_sock.getpeercert(binary_form=True)
                if der:
                    info["peer_cert_unverified"] = {
                        "sha256_der": hashlib.sha256(der).hexdigest(),
                        "der_len_bytes": len(der),
                    }
    except Exception as exc:
        info["unverified_probe_error"] = {
            "type": type(exc).__name__,
            "reason": str(exc),
        }

    return info


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_report_with_hashes(
    report_obj: dict[str, Any],
    markdown_text: str,
    json_path: Path,
    md_path: Path,
) -> dict[str, str]:
    """Сохраняет JSON и MD в UTF-8 без BOM и возвращает SHA-256 от сырых байтов."""
    json_bytes = json.dumps(report_obj, ensure_ascii=False, indent=2).encode("utf-8")
    md_bytes = markdown_text.encode("utf-8")

    json_path.write_bytes(json_bytes)
    md_path.write_bytes(md_bytes)

    return {
        "json_path": str(json_path),
        "json_sha256": sha256_bytes(json_bytes),
        "json_size_bytes": str(len(json_bytes)),
        "md_path": str(md_path),
        "md_sha256": sha256_bytes(md_bytes),
        "md_size_bytes": str(len(md_bytes)),
    }


if __name__ == "__main__":
    host = "arhiv1973b.github.io"
    port = 443
    print(f"Auditing TLS for {host}:{port}...")
    report = inspect_tls_chain(host, port)
    markdown = (
        f"# TLS Audit Report: {host}\n\n```json\n{json.dumps(report, indent=2)}\n```"
    )
    hashes = write_report_with_hashes(
        report, markdown, Path("report.json"), Path("report.md")
    )
    print(json.dumps(hashes, indent=2))
