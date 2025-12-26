import re

MIN_CHUNK_WORDS = 120
MAX_CHUNK_WORDS = 450

# Parent-level headings ONLY
HEADING_PATTERNS = [
    r'^[A-Z][A-Z\s\d\-:,]{4,}$',   # ALL CAPS headings
    r'^\d+(\.\d+)*\s+.+',          # 1. / 1.1 / 2.3 Title
    r'^.+:$'                       # Ends with :
]

# Sub-steps (these should NOT create new chunks)
SUBSTEP_PATTERNS = [
    r'^(Step|STEP)\s+\d+[:\-]?\s*.*',
    r'^\d+\)\s+.*',                # 1) Step
    r'^[a-zA-Z]\)\s+.*'            # a) Step
]


def is_heading(line: str) -> bool:
    line = line.strip()
    if len(line) < 4:
        return False

    # If it's a sub-step, DO NOT treat as heading
    for pattern in SUBSTEP_PATTERNS:
        if re.match(pattern, line):
            return False

    for pattern in HEADING_PATTERNS:
        if re.match(pattern, line):
            return True

    return False


def clean_title(title: str) -> str:
    title = re.sub(r'[:\-]+$', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip().title()


def heading_based_chunking(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    chunks = []
    current_title = "Introduction"
    buffer = []

    for line in lines:
        if is_heading(line):
            if buffer:
                chunks.extend(_finalize(current_title, " ".join(buffer)))
            current_title = clean_title(line)
            buffer = []
        else:
            buffer.append(line)

    if buffer:
        chunks.extend(_finalize(current_title, " ".join(buffer)))

    return chunks


def _finalize(title, text):
    words = text.split()

    if len(words) <= MAX_CHUNK_WORDS:
        return [{
            "title": title,
            "content": text
        }]

    out = []
    start = 0

    while start < len(words):
        part = words[start:start + MAX_CHUNK_WORDS]

        if len(part) < MIN_CHUNK_WORDS and out:
            out[-1]["content"] += " " + " ".join(part)
            break

        out.append({
            "title": title,
            "content": " ".join(part)
        })

        start += MAX_CHUNK_WORDS

    return out

