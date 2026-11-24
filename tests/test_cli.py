import hashlib
import transnational_verify


class PdfResponse:
    status_code = 200
    url = "https://apostila.gov.md/test"
    history = []
    headers = {"Content-Type": "application/pdf"}
    content = b"%PDF-1.7\n" + b"dummy pdf content"


def test_build_apostille_url():
    url = transnational_verify.build_apostille_url("IMWM44AZGX6N6", "2013073817848")
    assert url == (
        "https://apostila.gov.md/apostila/site/"
        "downloadApostila/apostileCode/IMWM44AZGX6N6/"
        "securityCode/2013073817848"
    )


def test_local_file_path(monkeypatch, tmp_path):
    monkeypatch.setattr(transnational_verify, "DOWNLOADS", tmp_path)
    monkeypatch.setattr(transnational_verify, "MANIFESTS", tmp_path)
    monkeypatch.setattr(
        transnational_verify.requests, "get", lambda *a, **k: PdfResponse()
    )

    result = transnational_verify.process_transnational_record("TEST", "12345")
    assert result["local_file"] == str(tmp_path / "TEST.pdf")


def test_manifest_created(monkeypatch, tmp_path):
    monkeypatch.setattr(transnational_verify, "DOWNLOADS", tmp_path)
    monkeypatch.setattr(transnational_verify, "MANIFESTS", tmp_path)
    monkeypatch.setattr(
        transnational_verify.requests, "get", lambda *a, **k: PdfResponse()
    )
    monkeypatch.setattr(
        transnational_verify,
        "quick_signature_check",
        lambda p: {"signed": False, "signature_count": 0},
    )

    transnational_verify.process_transnational_record("TEST", "123")
    manifest = tmp_path / "TEST_manifest.json"
    assert manifest.exists()


def test_manifest_fields(monkeypatch, tmp_path):
    monkeypatch.setattr(transnational_verify, "DOWNLOADS", tmp_path)
    monkeypatch.setattr(transnational_verify, "MANIFESTS", tmp_path)
    monkeypatch.setattr(
        transnational_verify.requests, "get", lambda *a, **k: PdfResponse()
    )
    monkeypatch.setattr(
        transnational_verify,
        "quick_signature_check",
        lambda p: {"signed": True, "signature_count": 1},
    )

    result = transnational_verify.process_transnational_record("ABC", "123")
    assert "sha256" in result
    assert "pdf_signature" in result
    assert result["pdf_signature"]["signed"] is True


def test_sha256_matches_content(monkeypatch, tmp_path):
    monkeypatch.setattr(transnational_verify, "DOWNLOADS", tmp_path)
    monkeypatch.setattr(transnational_verify, "MANIFESTS", tmp_path)
    monkeypatch.setattr(
        transnational_verify.requests, "get", lambda *a, **k: PdfResponse()
    )
    monkeypatch.setattr(
        transnational_verify,
        "quick_signature_check",
        lambda p: {"signed": False, "signature_count": 0},
    )

    result = transnational_verify.process_transnational_record("TEST", "123")
    expected = hashlib.sha256(PdfResponse.content).hexdigest()
    assert result["sha256"] == expected
