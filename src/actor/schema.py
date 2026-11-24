from __future__ import annotations
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field


class Error(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "error", "critical"]


class RetryPolicy(BaseModel):
    attempt: int
    max_attempts: int
    delay_seconds: int = 0
    next_action: Optional[str] = None


class ComponentA(BaseModel):
    page_type: Literal["apostille"] = "apostille"
    ocr_required: Literal[True] = True
    apostille_number: Optional[str] = None
    security_code: Optional[str] = None
    country: Optional[str] = None
    signatory_name: Optional[str] = None
    signatory_capacity: Optional[str] = None
    issuing_authority: Optional[str] = None
    apostille_authority: Optional[str] = None
    apostille_date: Optional[str] = None
    apostille_officer: Optional[str] = None
    digital_signature_present: bool = False


class ComponentB(BaseModel):
    page_type: Literal["source_document"] = "source_document"
    ocr_required: Literal[False] = False
    ocr_attempted: bool = False
    ocr_confidence: Optional[float] = None
    manual_validation_required: bool = False
    bitmap_preservation: bool = True
    page_sha256: Optional[str] = None
    signature_detected: Optional[bool] = None
    seal_detected: Optional[bool] = None
    watermark_detected: Optional[bool] = None


class ComponentC(BaseModel):
    page_type: Literal["verification_record"] = "verification_record"
    required: Literal[True] = True
    physical_page_present: bool = True
    virtual_reconstruction_allowed: bool = True
    status: Literal["present", "missing", "recovered", "virtual"]
    verification_source: Optional[
        Literal["html", "pdf", "screenshot", "manual", "virtual_reconstruction"]
    ] = None
    query: Optional[dict[str, Optional[str]]] = None
    verification_record: Optional[dict[str, Optional[str]]] = None


class DownloadInfo(BaseModel):
    status: Literal["not_attempted", "url_generated", "downloaded", "failed"]
    download_url: Optional[str] = None
    pdf_sha256: Optional[str] = None


class AuditInfo(BaseModel):
    A_required: Literal[True] = True
    B_required: Literal[True] = True
    C_required: Literal[True] = True
    virtual_c_allowed: Literal[True] = True


class ApostilleEvidenceBundle(BaseModel):
    pipeline_version: str
    bundle_status: Literal[
        "success", "partial_success", "retry", "manual_review", "fail"
    ]
    errors: List[Error] = []
    warnings: List[Error] = []
    retry: Optional[RetryPolicy] = None
    A: ComponentA
    B: ComponentB
    C: ComponentC
    download: DownloadInfo
    audit: AuditInfo

    # Forensic Metadata
    chain_of_custody: List[str] = []
    evidence_id: Optional[str] = None
    cas_object_id: Optional[str] = None
    cas_sha256: Optional[str] = None
