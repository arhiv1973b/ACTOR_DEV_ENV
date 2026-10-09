from sentence_transformers import SentenceTransformer, util
import json

# Инициализация многоязычной модели эмбеддингов
print("[*] Loading multilingual embedding model...")
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Фундаментальные юридические инварианты (базовые векторные константы)
fundamental_invariants = [
    "Безоговорочное признание единого государственного IDNP для любых вариантов транслитерации имени и фамилии",
    "Запрет произвольного удержания, заморозки и блокирования законных активов бенефициара на транзитных счетах",
    "Юридическая эквивалентность и тождественность лингвистических форм написания фамилии (MACHERET и MACERET) для одного лица",
    "Обязательность и высшая юридическая сила научных заключений Института филологии (Aviz № 269) при установлении персональной идентичности",
    "Недопустимость использования процедур KYC и SWIFT в качестве предлога для незаконного присвоения или отчуждения средств",
]

# Преобразуем инварианты в векторное пространство
invariant_embeddings = model.encode(fundamental_invariants, convert_to_tensor=True)

# Заявления банковской бюрократии и коллизионные тезисы для проверки на ничтожность
test_claims = [
    "Банк отказывает в зачислении средств 25 210 256.15 MDL из-за разницы в одну букву между MACHERET и MACERET",
    "Система комплаенса и KYC трактует владельца IDNP 2000001159655 и получателя MACHERET как двух разных людей чтобы избежать необоснованного обогащения",
    "Агентство государственных услуг официально подтвердило идентичность и выдало паспорт на транслитерацию MACHERET с привязкой к неизменному IDNP",
    "Денежные средства зависли на невыясненных счетах банка без отражения в официальных выписках клиента",
]

print("\n=== VECTOR COLLISION & NULLITY ANALYSIS ===")
analysis_results = []

for claim in test_claims:
    claim_embedding = model.encode(claim, convert_to_tensor=True)
    cos_scores = util.cos_sim(claim_embedding, invariant_embeddings)[0]

    max_score = cos_scores.max().item()
    best_invariant_idx = cos_scores.argmax().item()
    best_invariant = fundamental_invariants[best_invariant_idx]

    # Оценка соответствия / ничтожности
    # Если сходство с защитными инвариантами низкое, либо утверждение нарушает инвариант -> юридическая ничтожность
    status = (
        "VALID (Соответствует константам)"
        if max_score > 0.65
        else "NULL & VOID (Юридически ничтожно / Произвол)"
    )

    print(f'\nТезис: "{claim}"')
    print(f" -> Максимальное сходство с инвариантом: {max_score:.4f}")
    print(f" -> Ближайший инвариант: {best_invariant}")
    print(f" -> Статус: {status}")

    analysis_results.append(
        {
            "claim": claim,
            "max_similarity": max_score,
            "closest_invariant": best_invariant,
            "status": status,
        }
    )

# Сохранение результатов анализа
output_path = r"H:\ACTOR_DEV_ENV\analysis_temp\vector_collision_analysis.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(analysis_results, f, indent=2, ensure_ascii=False)

print(f"\n[+] Vector collision analysis saved to {output_path}")
