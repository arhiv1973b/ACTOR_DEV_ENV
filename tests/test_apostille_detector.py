import pytest
from actor.ocr_utils import (
    detect_document_type,
    should_force_ocr,
)

# NOTE: Updated imports to match src/actor/ocr_utils.py location


def test_detect_apostille_romanian():
    text = """
    APOSTILA
    Conventia de la Haga
    5 octombrie 1961
    Security code: 2013073817848
    """
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_detect_apostille_english():
    text = """
    APOSTILLE
    Convention de La Haye
    5 October 1961
    """
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_detect_apostille_russian():
    text = """
    АПОСТИЛЬ
    Гаагская Конвенция
    5 октября 1961 года
    """
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_detect_by_security_code():
    text = "Security code: 2013074052736"
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_detect_by_apostila_domain():
    text = "Verification URL: https://apostila.gov.md/apostila/site/"
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_non_apostille_document():
    text = """
    CURTEA SUPREMA DE JUSTITIE
    Dosar nr. 21-40/2021
    Hotarare
    """
    assert detect_document_type(text, "test.pdf") == "other"


def test_empty_text():
    assert detect_document_type("", "test.pdf") == "other"


def test_random_text():
    text = "Lorem ipsum dolor sit amet."
    assert detect_document_type(text, "test.pdf") == "other"


def test_apostille_with_noise():
    text = "Document scan APOSTILA random text 5 octombrie 1961 random text"
    assert detect_document_type(text, "test.pdf") == "apostille"


@pytest.mark.parametrize("page", [2, 4, 6, 8, 10, 12])
def test_force_ocr_even_pages(page):
    assert should_force_ocr(page, "apostille") is True


@pytest.mark.parametrize("page", [1, 3, 5, 7, 9])
def test_no_force_ocr_odd_pages(page):
    assert should_force_ocr(page, "apostille") is False


def test_other_document_no_forced_ocr():
    for page in range(1, 15):
        assert should_force_ocr(page, "other") is False


def test_case_insensitive_detection():
    text = "apostila conventia de la haga 5 octombrie 1961"
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_security_code_only():
    text = "Security Code: 2013073817848"
    assert detect_document_type(text, "test.pdf") == "apostille"


def test_apostille_url_only():
    text = "apostila.gov.md"
    assert detect_document_type(text, "test.pdf") == "apostille"
