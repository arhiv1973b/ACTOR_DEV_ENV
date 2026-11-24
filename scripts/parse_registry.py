import json
import re


def parse_registry(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    entries = []
    i = 0
    while i < len(lines):
        try:
            # Find the start of an entry (a number)
            if lines[i].isdigit() and int(lines[i]) > 0:
                num = lines[i]
                i += 1

                # Extract fields based on the fixed pattern
                apostille = lines[i]
                i += 1

                security_code = lines[i]
                i += 1

                case = lines[i]
                i += 1

                signer = lines[i]
                # Some signers might span multiple lines like "Мирон Алёна\nИ.О.\nвицепрезидента"
                # Need to detect the dates
                while not re.match(r"\d{2}\.\d{2}\.\d{4}", lines[i + 1]):
                    signer += " " + lines[i + 1]
                    i += 1
                i += 1

                date1 = lines[i]
                i += 1

                date2 = lines[i]
                i += 1

                # Skip 'Скачать'
                if lines[i] == "Скачать":
                    i += 1

                entries.append(
                    {
                        "num": int(num),
                        "apostille": apostille,
                        "security_code": security_code,
                        "case": case,
                        "signer": signer,
                        "dates": f"{date1} / {date2}",
                    }
                )
            else:
                i += 1
        except Exception as e:
            i += 1
            continue
    return entries


entries = parse_registry(r"H:\ACTOR_DEV_ENV\registry_text.txt")
with open(
    r"H:\ACTOR_DEV_ENV\evidence\full_apostille_registry.json", "w", encoding="utf-8"
) as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)
print(f"Parsed {len(entries)} entries.")
