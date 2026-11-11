import datetime
import crypto_utils
from crypto_utils import canonical_record_hash, calculate_custody_root_hash


def validate_chain(chain: list, expected_object_ids: set = None) -> list:
    """Validate chain integrity and return a list of error strings."""
    errors = []
    previous_record_hash = None
    custody_ids = set()

    for index, record in enumerate(chain):
        cid = record.get("custody_id")

        # 1. Missing custody_id
        if cid is None:
            errors.append("missing custody_id")
            cid = f"index-{index}"
        elif cid in custody_ids:
            errors.append(f"Duplicate custody_id: {cid}")
        else:
            custody_ids.add(cid)

        # 2. Validate current record integrity
        actual_hash = record.get("record_sha256")

        if actual_hash is None:
            errors.append(f"{cid}: missing record_sha256")
        elif not crypto_utils.validate_sha256(actual_hash):
            errors.append(f"{cid}: invalid record_sha256 format")
        else:
            expected_hash = crypto_utils.canonical_record_hash(record)
            if actual_hash.lower() != expected_hash.lower():
                errors.append(f"{cid}: record_sha256 mismatch")
            else:
                validated_record_hash = actual_hash.lower()

        # 3. Validate chain links
        if index > 0:
            prev_cid = record.get("previous_custody_id")
            if prev_cid is None:
                errors.append(f"{cid}: missing previous_custody_id")
            elif prev_cid not in custody_ids:
                errors.append(f"{cid}: unknown previous_custody_id")

            actual_prev_hash = record.get("previous_record_sha256")
            if actual_prev_hash is None:
                errors.append(f"{cid}: missing previous_record_sha256")
            elif not crypto_utils.validate_sha256(actual_prev_hash):
                errors.append(f"{cid}: invalid previous_record_sha256 format")
            elif previous_record_hash is None:
                errors.append(
                    f"{cid}: chain broken because previous record hash is unavailable"
                )
            elif actual_prev_hash.lower() != previous_record_hash.lower():
                errors.append(f"{cid}: previous_record_sha256 mismatch")

        # 4. Timestamp
        timestamp = record.get("timestamp")
        if timestamp is None:
            errors.append(f"{cid}: missing timestamp")
        elif not isinstance(timestamp, str):
            errors.append(f"{cid}: invalid timestamp")
        else:
            try:
                # Basic check for Z or offset
                if not (
                    timestamp.endswith("Z")
                    or "+" in timestamp
                    or "-" in timestamp
                    and timestamp.count("-") > 2
                ):
                    errors.append(f"{cid}: timestamp missing timezone")
                else:
                    # Parse to ensure it's valid
                    datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{cid}: invalid timestamp")

        # 5. Object ID
        if expected_object_ids is not None:
            obj_id = record.get("object_id")
            if obj_id not in expected_object_ids:
                errors.append(f"{cid}: unknown object")

        # 6. Result
        if record.get("result") not in ["success", "failure"]:
            errors.append(f"{cid}: invalid result")

        previous_record_hash = actual_hash.lower() if actual_hash else None

    return errors
