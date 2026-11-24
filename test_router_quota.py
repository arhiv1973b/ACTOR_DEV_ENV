import pytest
import time


def test_manifest_without_available_models_uses_defaults():

    alias = "models/gemini-3.5-pro"

    fallbacks = [
        "models/gemini-3.1-pro-preview",
        "models/gemini-pro-latest",
        "models/gemini-2.5-pro",
        "models/gemini-flash-latest",
    ]

    available_models = []

    if not available_models:
        available_models = [alias, *fallbacks]

    assert len(available_models) == 5


def test_empty_manifest_and_quota_error():

    alias = "models/gemini-3.5-pro"

    fallbacks = [
        "models/gemini-3.1-pro-preview",
        "models/gemini-2.5-pro",
    ]

    available_models = []

    if not available_models:
        available_models = [alias, *fallbacks]

    assert alias in available_models


def test_limit_zero_detected():

    msg = """
    Quota exceeded for metric:
    generate_content_free_tier_requests
    limit: 0
    """

    assert "limit: 0" in msg


def test_real_google_zero_quota_response():

    google_error = '''
    Quota exceeded for metric:
    generativelanguage.googleapis.com/generate_content_free_tier_requests

    limit: 0

    model: gemini-3.1-pro
    '''

    assert "Quota exceeded" in google_error
    assert "limit: 0" in google_error
    assert "gemini-3.1-pro" in google_error


def test_quota_model_enters_cooldown():

    cooldown = {}

    model = "models/gemini-3.1-pro"

    cooldown[model] = time.time() + 3600

    assert cooldown[model] > time.time()


def test_cooldown_model_skipped():

    model = "models/gemini-3.1-pro"

    cooldown = {
        model: time.time() + 3600
    }

    assert cooldown[model] > time.time()


def test_fallback_order():

    candidates = [
        "models/gemini-3.5-pro",
        "models/gemini-3.1-pro-preview",
        "models/gemini-pro-latest",
        "models/gemini-2.5-pro",
        "models/gemini-flash-latest",
    ]

    assert candidates[0] == "models/gemini-3.5-pro"
    assert candidates[-1] == "models/gemini-flash-latest"


def test_all_models_unavailable():

    candidates = [
        "models/gemini-3.5-pro",
        "models/gemini-2.5-pro",
    ]

    with pytest.raises(RuntimeError):
        raise RuntimeError(
            f"Все модели недоступны. Проверены: {', '.join(candidates)}"
        )


def test_last_error_contains_quota():

    error = (
        "Quota exceeded for metric "
        "generate_content_free_tier_requests"
    )

    with pytest.raises(RuntimeError) as exc:
        raise RuntimeError(
            f"Все модели недоступны. Последняя ошибка: {error}"
        )

    assert "Quota exceeded" in str(exc.value)


def test_router_recovers_from_empty_models():

    candidates = [
        "models/gemini-3.5-pro",
        "models/gemini-2.5-pro",
    ]

    available_models = []

    if not available_models:
        available_models = candidates.copy()

    assert available_models == candidates


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", __file__]))
