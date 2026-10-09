import os
import json

JSON_REPORT = r"H:\ACTOR_DEV_ENV\VECTOR_ENTITY_EXTRACTION_REPORT.json"
MD_REPORT = r"H:\ACTOR_DEV_ENV\VECTOR_ENTITY_EXTRACTION_REPORT.md"


def main():
    if not os.path.exists(JSON_REPORT):
        print(f"JSON report not found: {JSON_REPORT}")
        return

    with open(JSON_REPORT, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("extracted_records", [])
    search_samples = data.get("search_samples", [])

    lines = [
        "# FORENSIC VECTOR & ENTITY EXTRACTION REPORT",
        f"**Total Records Analyzed:** {len(records)}",
        "",
        "## Semantic Search & Extracted Entities Summary",
        "| Query | File Name | Similarity | IDNP | Amounts | Aviz | Courts |",
        "|---|---|---|---|---|---|---|",
    ]

    for sample in search_samples:
        q = sample.get("query", "")
        score = f"{sample.get('score', 0):.4f}"
        fname = sample.get("filename", "")
        ent = sample.get("entities", {})
        idnp = ", ".join(ent.get("idnp", [])) or "—"
        amounts = ", ".join(ent.get("amounts", [])) or "—"
        aviz = ", ".join(ent.get("aviz", [])) or "—"
        courts = ", ".join(ent.get("courts", [])) or "—"

        lines.append(
            f"| {q} | `{fname}` | {score} | {idnp} | {amounts} | {aviz} | {courts} |"
        )

    lines.extend(
        [
            "",
            "## Top Extracted Entities Matrix (Sample)",
            "| File Name | Summary | IDNP | Amounts | Aviz | Courts |",
            "|---|---|---|---|---|---|",
        ]
    )

    # Show first 20 records with entities or general records
    count = 0
    for rec in records:
        ent = rec.get("extracted_entities", {})
        idnp = ", ".join(ent.get("idnp", []))
        amounts = ", ".join(ent.get("amounts", []))
        aviz = ", ".join(ent.get("aviz", []))
        courts = ", ".join(ent.get("courts", []))

        # Include if any entity found or first 15
        if idnp or amounts or aviz or courts or count < 15:
            fname = rec.get("filename", "")
            summary = rec.get("summary", "") or "—"
            lines.append(
                f"| `{fname}` | {summary[:60]} | {idnp or '—'} | {amounts or '—'} | {aviz or '—'} | {courts or '—'} |"
            )
            count += 1
            if count >= 30:
                break

    with open(MD_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Markdown report generated successfully at {MD_REPORT}")


if __name__ == "__main__":
    main()
