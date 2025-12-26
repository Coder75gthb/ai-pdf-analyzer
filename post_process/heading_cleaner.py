import re

def is_valid_heading(text: str) -> bool:
    text = text.strip()

    # Too short or empty
    if len(text) < 6:
        return False

    # Must contain lowercase letters (real language)
    if not re.search(r'[a-z]', text):
        return False

    # Reject OCR junk patterns
    junk_patterns = [
        r'^[A-Z0-9\s\-_=~]{8,}$',
        r'.*TT.*TT.*',
        r'.*OOO.*',
        r'^[0-9\s]+$'
    ]

    for p in junk_patterns:
        if re.match(p, text):
            return False

    return True


def clean_notes(notes: str) -> str:
    lines = notes.split("\n")
    cleaned = []

    for line in lines:
        line_strip = line.strip()

        if line_strip.startswith("📌"):
            heading = line_strip.replace("📌", "").strip()
            if is_valid_heading(heading):
                cleaned.append(f"## {heading}")
            else:
                continue
        else:
            cleaned.append(line)

    return "\n".join(cleaned)


# alias (this avoided your earlier import crash)
clean_headings = clean_notes
