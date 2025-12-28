# llm/groq_maths_summarizer.py

import os
import re
import hashlib
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 400

# ------------------ STRICT THEORY MATCH ------------------

ALLOWED_START_PATTERNS = re.compile(
    r"(?i)\b(definition|theorem|lemma|corollary|property)\b"
)

NUMBERING_PATTERN = r"\b(definition|theorem|lemma|corollary|property)\s*\d+(\.\d+)*\b"

VALID_FORMULA_PATTERN = re.compile(r"[=∧∨→≤≥⊆∈]")

# Kill proof / example / explanation language
KILL_LANGUAGE = re.compile(
    r"\b("
    r"proof|from\s*\(|suppose|then\s|hence|therefore|subtracting|"
    r"example|solution|question|case\s|we\s+get|let\s|end\s+of\s+proof|"
    r"sop|pos|minterms|maxterms"
    r")\b",
    re.I
)

#  NEW: kill admin / junk sections
ADMIN_JUNK = re.compile(
    r"\b(reference|references|not\s+applicable|bibliography)\b",
    re.I
)

#  NEW: kill enumerated proof chains
ENUMERATED_CHAIN = re.compile(
    r"(\(\d+\)|\b(i|ii|iii|iv|v|vi|vii|viii|ix|x)\.)",
    re.I
)

# ------------------ DEDUP ------------------

_seen = set()

def _normalize_line(line: str) -> str:
    line = re.sub(NUMBERING_PATTERN, "", line, flags=re.I)
    line = re.sub(r"\s+", " ", line)
    return line.strip().lower()

def _dedup_lines(lines):
    out = []
    for l in lines:
        h = hashlib.sha256(_normalize_line(l).encode()).hexdigest()
        if h not in _seen:
            _seen.add(h)
            out.append(l)
    return out

# ------------------ PROMPT ------------------

SYSTEM_PROMPT = """
You extract ONLY EXAM-READY MATHEMATICS THEORY.

RULES:
- Output ONLY definitions (1 line) and final formulas
- NO proofs
- NO derivations
- NO explanations
- NO examples
- NO questions
- NO repetition

FORMAT:
DEFINITION:
FORMULAS / RESULTS:
"""

# ------------------ MAIN ------------------

def summarize_math_topic(title: str, text: str) -> str:
    if not text or len(text) < 120:
        return ""

    if not ALLOWED_START_PATTERNS.search(text) and not VALID_FORMULA_PATTERN.search(text):
        return ""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.0,
        max_tokens=MAX_TOKENS,
    )

    raw = response.choices[0].message.content.strip()
    if not raw:
        return ""

    cleaned_lines = []

    for line in raw.splitlines():
        line = line.strip()

        if len(line) < 15:
            continue

        #  Kill admin junk
        if ADMIN_JUNK.search(line):
            continue

        #  Kill proofs / explanations
        if KILL_LANGUAGE.search(line):
            continue

        #  Kill enumerated algebra chains
        if ENUMERATED_CHAIN.search(line):
            continue

        #  Kill long English-only lines (paragraph spam)
        if not VALID_FORMULA_PATTERN.search(line) and len(line.split()) > 18:
            continue

        # Keep only definitions or real formulas
        if ALLOWED_START_PATTERNS.search(line) or VALID_FORMULA_PATTERN.search(line):
            cleaned_lines.append(line)

    cleaned_lines = _dedup_lines(cleaned_lines)

    if not cleaned_lines:
        return ""

    return "\n".join(cleaned_lines)
