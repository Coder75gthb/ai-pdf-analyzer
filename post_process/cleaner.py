import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    lines = text.split("\n")
    cleaned = []
    seen = set()

    for line in lines:
        raw = line.rstrip()

        if not raw.strip():
            cleaned.append("")
            continue

        # remove OCR junk ONLY
        if re.match(r'^[A-Z0-9\s\-\_=~]{10,}$', raw):
            continue

        key = raw.lower()
        if key in seen:
            continue
        seen.add(key)

        cleaned.append(raw)

    return "\n".join(cleaned).strip()
