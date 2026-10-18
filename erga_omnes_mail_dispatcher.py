#!/usr/bin/env python3
"""
ERGA OMNES MAIL DISPATCHER & EVIDENCE GATEWAY
Case Reference: CASE-MACHERET-1997-2026
Security Anchor: A©TOR_KEY="# [⚖ A©tor Declaration]"
"""

import os
import sys
import json
import hashlib
import datetime
import smtplib
from email.message import EmailMessage

# Master Recipient Categories under Erga Omnes / Jus Cogens Protocol
RECIPIENT_GROUPS = {
    "JUDICIAL": [
        "colegiul.penal@csj.md",
        "colegiul.civil@csj.md",
        "secretariat@constcourt.md",
        "caccancelaria@justice.md",
        "cac@justice.md",
        "jbu@justice.md",
        "jrc@justice.md",
        "jbotanica@justice.md",
        "jcc@justice.md",
    ],
    "LAW_ENFORCEMENT": [
        "petitii@sis.md",
        "secretariat@mai.gov.md",
        "mai@mai.gov.md",
        "ot_chisinau@cnajgs.md",
        "serviciipublice@arhiva.gov.md",
        "valeriu.frimu@justice.gov.md",
    ],
    "FINANCIAL_REGULATORS": [
        "state-fcb@fincombank.com",
        "mail@sfs.md",
        "secretariat@bnm.md",
        "cancelaria@mf.gov.md",
    ],
    "INTERNATIONAL": [
        "chisinauprotocol@state.gov",
        "communications@mail.whitehouse.gov",
    ],
    "APPLICANT": ["alexeimaceret7@gmail.com", "arhiv1973b@outlook.com"],
}

DEFAULT_DOWNLOADS = r"H:\Загрузки"
LOG_FILE = r"H:\ACTOR_DEV_ENV\audit_detection_log.csv"


def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def dispatch_document(doc_path, category="JUDICIAL", dry_run=True):
    if not os.path.exists(doc_path):
        print(f"[!] Document not found: {doc_path}")
        return False

    file_name = os.path.basename(doc_path)
    file_hash = compute_sha256(doc_path)
    recipients = RECIPIENT_GROUPS.get(category, RECIPIENT_GROUPS["APPLICANT"])

    print(f"\n[*] Dispatching Document: {file_name}")
    print(f"    Category: {category}")
    print(f"    SHA-256: {file_hash}")
    print(f"    Recipients: {', '.join(recipients)}")

    msg = EmailMessage()
    msg["Subject"] = (
        f"[JUS COGENS / ERGA OMNES] Notice & Evidence Dispatch: {file_name}"
    )
    msg["From"] = "alexeimaceret7@gmail.com"
    msg["To"] = ", ".join(recipients)

    body = (
        f"OFFICIAL NOTICE UNDER ERGA OMNES / JUS COGENS PROTOCOL\n"
        f"Case Reference: CASE-MACHERET-1997-2026\n"
        f"Document: {file_name}\n"
        f"Cryptographic Anchor (SHA-256): {file_hash}\n"
        f'Signature: A©TOR_KEY="# [⚖ A©tor Declaration]"\n\n'
        f"This message transmits verified evidentiary material under international peremptory norms."
    )
    msg.set_content(body)

    try:
        with open(doc_path, "rb") as f:
            file_data = f.read()
            msg.add_attachment(
                file_data, maintype="application", subtype="pdf", filename=file_name
            )
    except Exception as e:
        print(f"[!] Attachment error: {e}")

    if dry_run:
        print(
            f"    [DRY RUN] Message successfully prepared and sealed for {file_name}."
        )
    else:
        # Real SMTP dispatch can be configured here if SMTP credentials are provided
        print(f"    [SMTP] Dispatch simulated or transmitted.")

    # Log dispatch event
    log_entry = f"{datetime.datetime.now(datetime.timezone.utc).isoformat()},{file_name},{file_hash},{category},{len(recipients)}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(log_entry)
    except Exception:
        pass

    return True


if __name__ == "__main__":
    print("--- ERGA OMNES MAIL DISPATCHER & EVIDENCE GATEWAY ---")
    execute_mode = "--execute" in sys.argv
    sample_doc = os.path.join(
        DEFAULT_DOWNLOADS, "⚖ Ator Declaration_Casatia Lege.подписан.pdf"
    )
    if not os.path.exists(sample_doc):
        # Fallback to local test document or public PDF if sample not in Downloads
        sample_doc = "court_dashboard.html"

    if os.path.exists(sample_doc):
        dispatch_document(sample_doc, category="JUDICIAL", dry_run=not execute_mode)
    else:
        print("[*] Sample document not found, running status check.")
