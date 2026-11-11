import jcs
import hashlib
import copy
import re

SHA256_RE = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)


def sha256_jcs(obj: dict) -> str:
    """Calculate SHA-256 hash using JCS (RFC 8785)."""
    canonical_bytes = jcs.canonicalize(obj)
    return hashlib.sha256(canonical_bytes).hexdigest()


def canonical_record_hash(record: dict) -> str:
    """Calculate canonical hash for a record, excluding 'record_sha256'."""
    payload = copy.deepcopy(record)
    payload.pop("record_sha256", None)
    canonical = jcs.canonicalize(payload)
    return hashlib.sha256(canonical).hexdigest()


def object_sha256(obj) -> str:
    """Generic SHA-256 hash of an object using JCS."""
    return hashlib.sha256(jcs.canonicalize(obj)).hexdigest()


def validate_sha256(value: str) -> bool:
    """Validate SHA-256 hash format (64 hex characters)."""
    if value is None or not isinstance(value, str):
        return False
    return bool(SHA256_RE.fullmatch(value))


def calculate_custody_root_hash(chain: list) -> str:
    """Calculate root hash of a custody chain with strict validation."""
    records = []
    for r in chain:
        hash_value = r.get("record_sha256")
        if hash_value is None:
            raise ValueError(
                f"Missing record_sha256 for {r.get('custody_id', 'Unknown')}"
            )
        if not validate_sha256(hash_value):
            raise ValueError(
                f"Invalid record_sha256 format for {r.get('custody_id', 'Unknown')}"
            )
        records.append({"custody_id": r["custody_id"], "record_sha256": hash_value})

    payload = {
        "algorithm": "SHA-256",
        "canonicalization": "RFC8785-JCS",
        "records": records,
    }

    return sha256_jcs(payload)


def verify_record(record: dict) -> bool:
    """Verify record hash integrity."""
    expected = canonical_record_hash(record)
    actual = record.get("record_sha256")
    if actual is None or not validate_sha256(actual):
        return False
    return actual.lower() == expected.lower()
