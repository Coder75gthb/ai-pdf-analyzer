# chunking/topic_chunking.py

import re

MAX_TOPIC_SIZE = 4000


def _normalize_pages(pages):
    if isinstance(pages, dict):
        return [str(v) for v in pages.values() if v]
    if isinstance(pages, list):
        return [str(p) for p in pages if p]
    if isinstance(pages, str):
        return [pages]
    return []


def _is_heading(line):
    line = line.strip()
    if not line:
        return False
    if re.match(r"^\d+(\.\d+)*\s+", line):
        return True
    if line.isupper() and len(line) <= 80:
        return True
    return False


def topic_wise_chunk(pages):
    pages = _normalize_pages(pages)
    topics = []
    current_topic = "GENERAL"
    buffer = ""

    def flush():
        nonlocal buffer
        if buffer.strip():
            topics.append({"topic": current_topic, "text": buffer.strip()})
        buffer = ""

    for page in pages:
        for line in page.splitlines():
            if _is_heading(line):
                flush()
                current_topic = line.strip()
            else:
                buffer += line + "\n"

            if len(buffer) >= MAX_TOPIC_SIZE:
                flush()

    flush()
    return topics
