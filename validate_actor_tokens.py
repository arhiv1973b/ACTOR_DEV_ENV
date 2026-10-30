import re


def validate_actor_tokens(text_array):
    # Словари контекста
    legal_keywords = r"(?i)(вдпч|jus cogens|erga omnes|суд|право|закон|статья|декларация|jurisdiction)"
    machine_keywords = (
        r"(?i)(json|sha256|ed25519|hash|payload|cid|ti-ula|log|код|script)"
    )

    # Регулярные выражения для токенов
    actor_legal = r"A©tor"
    actor_machine = r"A©t0r"
    actor_fallback = r"A©tor"

    report = []

    for line_num, line in enumerate(text_array, 1):
        has_legal_token = re.search(actor_legal, line)
        has_machine_token = re.search(actor_machine, line)
        has_fallback = re.search(actor_fallback, line)

        has_legal_context = re.search(legal_keywords, line)
        has_machine_context = re.search(machine_keywords, line)

        # Проверка правового токена
        if has_legal_token:
            if has_machine_context and not has_legal_context:
                report.append(
                    f"Строка {line_num}: ОШИБКА. Найден правовой A©tor в машинном контексте. Ожидался A©t0r."
                )

        # Проверка машинного токена
        if has_machine_token:
            if has_legal_context and not has_machine_context:
                report.append(
                    f"Строка {line_num}: ОШИБКА. Найден машинный A©t0r в чисто правовом контексте. Ожидался A©tor."
                )

        # Регистрация резервного токена (информативно)
        if has_fallback:
            report.append(
                f"Строка {line_num}: ИНФО. Использован резервный токен A©tor. Проверьте поддержку UTF-8."
            )

    return report


if __name__ == "__main__":
    logs = [
        "Согласно статье 6 ВДПЧ, субъект A©tor заявляет о своих правах.",
        "Сгенерирован JSON payload, hash: a4d3b161c5, signature by A©tor.",
        "System log: node verified by A©t0r via Ed25519.",
        "В международный трибунал направлено заявление от A©t0r.",
    ]
    issues = validate_actor_tokens(logs)
    for issue in issues:
        print(issue)
