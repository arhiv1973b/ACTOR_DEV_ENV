import copy
from crypto_utils import canonical_record_hash
from validate_chain import validate_chain


def make_record():
    return {
        "custody_id": "COC-000001",
        "timestamp": "2026-11-09T08:00:00Z",
        "action": "hash_verified",
        "object_id": "ATT-000001",
        "performed_by": "A©t0r",
        "tool": "verify_sha256.py",
        "result": "success",
        "previous_custody_id": None,
        "previous_record_sha256": None,
    }


def test_record_sha256_scenarios():
    print("[*] Running record_sha256 validation scenarios...")

    # 1. Valid
    record = make_record()
    record["record_sha256"] = canonical_record_hash(record)
    assert not validate_chain([record])

    # 2. Missing
    record = make_record()
    errors = validate_chain([record])
    assert "COC-000001: missing record_sha256" in errors

    # 3. None
    record = make_record()
    record["record_sha256"] = None
    errors = validate_chain([record])
    assert "COC-000001: missing record_sha256" in errors

    # 4. Empty
    record = make_record()
    record["record_sha256"] = ""
    errors = validate_chain([record])
    assert "COC-000001: invalid record_sha256 format" in errors

    # 5. Short
    record = make_record()
    record["record_sha256"] = "123"
    errors = validate_chain([record])
    assert "COC-000001: invalid record_sha256 format" in errors

    # 6. Non-hex
    record = make_record()
    record["record_sha256"] = "z" * 64
    errors = validate_chain([record])
    assert "COC-000001: invalid record_sha256 format" in errors

    # 7. Mismatch
    record = make_record()
    record["record_sha256"] = "0" * 64
    errors = validate_chain([record])
    assert "COC-000001: record_sha256 mismatch" in errors

    print("[+] All record_sha256 scenarios passed.")


def test_chain_link_scenarios():
    print("[*] Running chain link validation scenarios...")

    # 1. Valid two-record chain
    first = make_record()
    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()
    second["custody_id"] = "COC-000002"
    second["previous_custody_id"] = "COC-000001"
    second["previous_record_sha256"] = first["record_sha256"]
    second["record_sha256"] = canonical_record_hash(second)

    assert not validate_chain([first, second])

    # 2. Missing previous_record_sha256 in second record
    second_invalid = copy.deepcopy(second)
    del second_invalid["previous_record_sha256"]
    # Update hash after modifying the record
    second_invalid["record_sha256"] = canonical_record_hash(second_invalid)

    errors = validate_chain([first, second_invalid])
    assert "COC-000002: missing previous_record_sha256" in errors

    # 3. Invalid previous_record_sha256 format
    second_invalid = copy.deepcopy(second)
    second_invalid["previous_record_sha256"] = "123"
    second_invalid["record_sha256"] = canonical_record_hash(
        second_invalid
    )  # Valid hash
    errors = validate_chain([first, second_invalid])
    assert "COC-000002: invalid previous_record_sha256 format" in errors

    # 4. Previous hash unavailable
    # first record is missing hash, second references it
    first_invalid = make_record()  # No hash, this will cause error in first record anyway, but let's just make sure chain link fails too
    first_invalid["record_sha256"] = "f" * 64  # Force valid format to pass format check

    second_invalid = copy.deepcopy(second)
    second_invalid["previous_record_sha256"] = "f" * 64  # Needs to be something
    second_invalid["record_sha256"] = canonical_record_hash(second_invalid)

    # The first record validation will fail, and previous_record_hash will be None.
    # The validator skips records with errors, so previous_record_hash won't be set correctly.
    errors = validate_chain([first_invalid, second_invalid])
    # The error should be about 'previous record hash is unavailable'
    assert any("chain broken" in e for e in errors)

    # 5. Previous hash mismatch
    second_invalid = copy.deepcopy(second)
    second_invalid["previous_record_sha256"] = "f" * 64
    second_invalid["record_sha256"] = canonical_record_hash(second_invalid)
    errors = validate_chain([first, second_invalid])
    assert "COC-000002: previous_record_sha256 mismatch" in errors

    print("[+] All chain link scenarios passed.")


if __name__ == "__main__":
    test_record_sha256_scenarios()
    test_chain_link_scenarios()
    print("[*] All tests passed!")
