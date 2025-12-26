import re
from extract.pdf_extract import extract_text_from_pdf
from llm.groq_summarizer import summarize_topic

def trim_text_for_llm(text: str, max_chars: int = 3500) -> str:
    """
    Prevents token overflow for math-heavy PDFs
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars]

# =====================================================
# FINAL BULLET NORMALIZER (UNCHANGED)
# =====================================================
def normalize_bullets(text: str) -> str:
    """
    Guarantees: ONE IDEA PER BULLET
    """

    output = []
    SEPARATORS = r"[•·∙]"

    for line in text.split("\n"):
        line = line.strip()

        if not line.startswith("•"):
            output.append(line)
            continue

        content = line[1:].strip()
        normalized = re.sub(SEPARATORS, "|", content)
        parts = [p.strip() for p in normalized.split("|") if p.strip()]

        for part in parts:
            output.append("• " + part)

    return "\n".join(output)






# =====================================================
# 🧹 LINE DEDUPLICATION (MATH ONLY)
# =====================================================
def deduplicate_lines(text: str) -> str:
    seen = set()
    cleaned = []
    for line in text.splitlines():
        norm = line.strip()
        if norm and norm not in seen:
            seen.add(norm)
            cleaned.append(line)
    return "\n".join(cleaned)

def normalize_truth_tables(text: str) -> str:
    """
    Cleans inline truth tables rendered in one line
    Converts | p | q | T | F | format into readable rows
    """

    lines = []
    for line in text.split("\n"):

        if "Truth Table" in line and "|" in line:
            lines.append("Truth Table")
            continue

        # Skip markdown separator rows
        if set(line.replace("|", "").strip()) == {"-"}:
            continue

        # Detect table-like rows
        if "|" in line:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 2:
                lines.append("  ".join(cells))
            continue

        lines.append(line)

    return "\n".join(lines)

def deduplicate_chunks(chunks):
    seen = set()
    unique = []

    for item in chunks:
        text = item["text"] if isinstance(item, dict) else item
        key = hash(text.strip())

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


# =====================================================
# STREAMING PIPELINE (INTACT + SAFE ADDITIONS)
# =====================================================
def run_pipeline(pdf_path):
    chunks = extract_text_from_pdf(pdf_path)
    
    chunks = deduplicate_chunks(chunks)


    yield "🧠 Cooking notes...\n"

    previous_was_math = False

    for idx, item in enumerate(chunks):

        if isinstance(item, dict):
            chunk_text = item["text"]
        else:
            chunk_text = item

        if not chunk_text.strip():
            continue

       

        topic = f"Chunk {idx + 1}"

        safe_text = trim_text_for_llm(chunk_text)
        summary = summarize_topic(topic, safe_text)


        # Remove any LLM-inserted success message
        summary = summary.replace("✅ Notes generated successfully", "")

        # 🔒 FINAL BULLET NORMALIZATION (UNCHANGED)
        summary = normalize_bullets(summary)
        summary = normalize_truth_tables(summary)

        yield summary + "\n\n"

      

# =====================================================
# REQUIRED BY app.py — DO NOT RENAME
# =====================================================
def process_pdf_stream(pdf_path):
    return run_pipeline(pdf_path)

