import pytest

from validator import (
    validate_chain,
    calculate_custody_root_hash,
    canonical_record_hash,
)


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


#
# record_sha256
#


def test_valid_record_hash():
    record = make_record()

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert errors == []


def test_missing_record_sha256():
    record = make_record()

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("missing record_sha256" in e for e in errors)


def test_none_record_sha256():
    record = make_record()

    record["record_sha256"] = None

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("missing record_sha256" in e for e in errors)


def test_empty_record_sha256():
    record = make_record()

    record["record_sha256"] = ""

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("invalid record_sha256 format" in e for e in errors)


def test_short_record_sha256():
    record = make_record()

    record["record_sha256"] = "123"

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("invalid record_sha256 format" in e for e in errors)


def test_non_hex_record_sha256():
    record = make_record()

    record["record_sha256"] = "z" * 64

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("invalid record_sha256 format" in e for e in errors)


def test_record_sha256_mismatch():
    record = make_record()

    record["record_sha256"] = "0" * 64

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("record_sha256 mismatch" in e for e in errors)


#
# custody_id
#


def test_missing_custody_id():
    record = make_record()

    del record["custody_id"]

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("missing custody_id" in e for e in errors)


def test_duplicate_custody_id():
    first = make_record()
    second = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("Duplicate custody_id" in e for e in errors)


#
# previous_custody_id
#


def test_missing_previous_custody_id():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_record_sha256"] = first["record_sha256"]

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("missing previous_custody_id" in e for e in errors)


def test_unknown_previous_custody_id():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_custody_id"] = "COC-999999"

    second["previous_record_sha256"] = first["record_sha256"]

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("unknown previous_custody_id" in e for e in errors)


#
# previous_record_sha256
#


def test_missing_previous_record_sha256():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_custody_id"] = first["custody_id"]

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("missing previous_record_sha256" in e for e in errors)


def test_invalid_previous_record_sha256_format():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_custody_id"] = first["custody_id"]

    second["previous_record_sha256"] = "123"

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("invalid previous_record_sha256 format" in e for e in errors)


def test_chain_break_when_previous_hash_invalid():
    first = make_record()

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_custody_id"] = "COC-000001"

    second["previous_record_sha256"] = "f" * 64

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any(
        "chain broken because previous record hash is unavailable" in e for e in errors
    )


def test_previous_record_sha256_mismatch():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_custody_id"] = first["custody_id"]

    second["previous_record_sha256"] = "f" * 64

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("previous_record_sha256 mismatch" in e for e in errors)


#
# timestamp
#


def test_missing_timestamp():
    record = make_record()

    record["timestamp"] = None

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("missing timestamp" in e for e in errors)


def test_invalid_timestamp():
    record = make_record()

    record["timestamp"] = "2026-99-99T99:99:99Z"

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("invalid timestamp" in e for e in errors)


def test_timestamp_not_string():
    record = make_record()

    record["timestamp"] = 12345

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("invalid timestamp" in e for e in errors)


def test_timestamp_missing_timezone():
    record = make_record()

    record["timestamp"] = "2026-11-09T08:00:00"

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("timestamp missing timezone" in e for e in errors)


def test_timestamp_order_violation():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["timestamp"] = "2026-11-08T08:00:00Z"

    second["previous_custody_id"] = first["custody_id"]

    second["previous_record_sha256"] = first["record_sha256"]

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert any("timestamp order violation" in e for e in errors)


def test_equivalent_timezones():
    first = make_record()

    first["timestamp"] = "2026-11-09T12:00:00+02:00"

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["timestamp"] = "2026-11-09T11:00:00+01:00"

    second["previous_custody_id"] = first["custody_id"]

    second["previous_record_sha256"] = first["record_sha256"]

    second["record_sha256"] = canonical_record_hash(second)

    errors = validate_chain(
        [first, second],
        {"ATT-000001"},
    )

    assert not any("timestamp order violation" in e for e in errors)


#
# object_id
#


def test_unknown_object():
    record = make_record()

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"DIFFERENT_OBJECT"},
    )

    assert any("unknown object" in e for e in errors)


#
# result
#


def test_invalid_result():
    record = make_record()

    record["result"] = "INVALID"

    record["record_sha256"] = canonical_record_hash(record)

    errors = validate_chain(
        [record],
        {"ATT-000001"},
    )

    assert any("invalid result" in e for e in errors)


#
# root hash
#


def test_root_hash_fails_when_record_hash_missing():
    chain = [{"custody_id": "COC-000001"}]

    with pytest.raises(
        ValueError,
        match="Missing record_sha256",
    ):
        calculate_custody_root_hash(chain)


def test_root_hash_invalid_hash_format():
    chain = [
        {
            "custody_id": "COC-000001",
            "record_sha256": "123",
        }
    ]

    with pytest.raises(
        ValueError,
        match="Invalid record_sha256 format",
    ):
        calculate_custody_root_hash(chain)


def test_custody_root_hash_consistency():
    first = make_record()

    first["record_sha256"] = canonical_record_hash(first)

    second = make_record()

    second["custody_id"] = "COC-000002"

    second["previous_custody_id"] = first["custody_id"]

    second["previous_record_sha256"] = first["record_sha256"]

    second["record_sha256"] = canonical_record_hash(second)

    chain = [first, second]

    root1 = calculate_custody_root_hash(chain)

    root2 = calculate_custody_root_hash(chain)

    assert root1 == root2
