import re
from typing import List, Tuple


# =========================
# 1. MATH DETECTION LOGIC
# =========================

MATH_SYMBOLS = r"[=+\-*/^_∑∏∫√≤≥≠(){}\[\]]"

LATEX_TOKENS = [
    r"\\frac", r"\\sum", r"\\int", r"\\lim", r"\\log",
    r"\\sin", r"\\cos", r"\\tan",
    r"\bn!\b", r"\bC\s*\(", r"\bP\s*\("
]

DEFINITION_KEYWORDS = (
    "definition",
    "theorem",
    "lemma",
    "corollary",
    "proposition",
    "rule",
    "law"
)


def is_math_pdf(text: str) -> bool:
    """
    Robust detection of math-heavy PDFs.
    Returns True only if multiple math signals are present.
    """

    if not text or len(text) < 500:
        return False

    total_chars = len(text)

    # (A) Symbol density
    symbol_count = len(re.findall(MATH_SYMBOLS, text))
    symbol_density = symbol_count / total_chars

    # (B) Formula tokens
    token_hits = sum(len(re.findall(t, text)) for t in LATEX_TOKENS)

    # (C) Short symbolic lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    short_math_lines = 0

    for line in lines:
        if (
            len(line.split()) <= 8
            and re.search(MATH_SYMBOLS, line)
        ):
            short_math_lines += 1

    short_line_ratio = (
        short_math_lines / len(lines)
        if lines else 0
    )

    return (
        symbol_density > 0.03
        and token_hits >= 10
        and short_line_ratio > 0.35
    )


# =========================
# 2. EXTRACTION RULES
# =========================

def is_formula_line(line: str) -> bool:
    return (
        re.search(MATH_SYMBOLS, line)
        and len(line.split()) <= 10
    )


def is_definition_line(line: str) -> bool:
    return line.lower().startswith(DEFINITION_KEYWORDS)


def is_example_or_explanation(line: str) -> bool:
    drop_words = (
        "example",
        "proof",
        "consider",
        "suppose",
        "let us",
        "hence",
        "therefore",
        "we see",
        "solution",
        "illustration"
    )
    return line.lower().startswith(drop_words)


# =========================
# 3. CORE MATH REDUCER
# =========================

def reduce_math_content(text: str) -> str:
    """
    Keeps only:
    - standalone formulas
    - one-line definitions/theorems
    Drops everything else.
    """

    lines = [l.strip() for l in text.splitlines()]
    output: List[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if not line:
            i += 1
            continue

        # Drop examples / explanations
        if is_example_or_explanation(line):
            i += 1
            continue

        # One-line definition / theorem
        if is_definition_line(line):
            output.append(f"\n{line.upper()}")
            i += 1
            continue

        # Formula lines
        if is_formula_line(line):
            output.append(line)
            i += 1
            continue

        i += 1

    return "\n".join(dict.fromkeys(output))  # remove duplicates, preserve order


# =========================
# 4. PUBLIC API
# =========================

def analyze_math_pdf(text: str) -> Tuple[bool, str]:
    """
    Main entry point.

    Returns:
    - is_math_pdf (bool)
    - reduced_content (str) if math else original text
    """

    if is_math_pdf(text):
        reduced = reduce_math_content(text)
        return True, reduced

    return False, text
