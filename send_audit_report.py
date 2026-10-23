#!/usr/bin/env python3
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def load_env_file():
    for env_file in [".env", ".env.local", ".env.audit", ".env.audit.local"]:
        p = Path(env_file)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def send_audit_email():
    load_env_file()

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    mail_to = os.getenv("MAIL_TO", smtp_user)
    mail_from = os.getenv("MAIL_FROM", smtp_user)

    if not smtp_user or not smtp_password:
        print("[-] SMTP_USER or SMTP_PASSWORD not set. Skipping email notification.")
        return

    log_path = Path("audit.log")
    if not log_path.exists():
        print("[-] audit.log not found. Skipping email notification.")
        return

    msg = EmailMessage()
    msg["Subject"] = "ACTOR_DEV_ENV: Daily Audit & Repair Report"
    msg["From"] = mail_from
    msg["To"] = mail_to

    msg.set_content(
        "Please find attached the daily audit and repair report log for ACTOR_DEV_ENV."
    )

    with open(log_path, "rb") as f:
        file_data = f.read()
        msg.add_attachment(
            file_data, maintype="text", subtype="plain", filename="audit.log"
        )

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("[+] Audit report email sent successfully to", mail_to)
    except Exception as e:
        print(f"[-] Failed to send audit email: {e}")


if __name__ == "__main__":
    send_audit_email()
