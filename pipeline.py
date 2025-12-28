# pipeline.py

import re
from extract.pdf_extract import extract_text_from_pdf
from llm.groq_summarizer import summarize_topic
from llm.groq_maths_summarizer import summarize_math_topic


def trim_text_for_llm(text: str, max_chars: int = 2000) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) < 120:
        return ""
    return text[:max_chars]


def is_math_heavy(text: str) -> bool:
    math_symbols = [
        "=", "∑", "∫", "→", "≤", "≥", "∞",
        "^", "_", "!", "C(", "P(", "\\frac"
    ]
    return sum(text.count(s) for s in math_symbols) >= 2


def run_pipeline(pdf_path):
    chunks = extract_text_from_pdf(pdf_path)
    seen = set()

    for idx, item in enumerate(chunks):
        raw = item["text"] if isinstance(item, dict) else item
        safe = trim_text_for_llm(raw)
        if not safe:
            continue

        if is_math_heavy(safe):
            summary = summarize_math_topic(f"Chunk {idx+1}", safe)
        else:
            summary = summarize_topic(f"Chunk {idx+1}", safe)

        if not summary:
            continue

        key = re.sub(r"\W+", "", summary.lower())[:120]
        if key in seen:
            continue
        seen.add(key)

        yield summary + "\n\n"


def process_pdf_stream(pdf_path):
    return run_pipeline(pdf_path)
