from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 700

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are an EXAM NOTES GENERATOR.

CRITICAL MATH RULE:
- NEVER introduce examples, applications, or topics not explicitly present
- If content is symbolic or formula-heavy, summarize ONLY definitions and results
- DO NOT add physics, electronics, circuits, or real-world interpretations

Your goal:
- Convert raw PDF/text into CLEAN, EXAM-READY NOTES
- Short, crisp, structured
- NO repetition
- NO textbook-style paragraphs

STRICT RULES (MANDATORY):

1. HEADERS
- BIG, BOLD, UNDERLINED
- Do NOT number
- Skip empty headers

2. BULLETS
- One idea per bullet
- NO bullet stacking on same line
- Exam-focused only

3. TABLES (VERY IMPORTANT)
- USE TABLES when:
  • differences / comparisons are mentioned
  • advantages vs disadvantages
  • instruction formats / state tables
  • modes, signals, architectures
- DO NOT convert everything into tables

4. CODE / RTN / STATE TABLES
- Use MONOSPACE blocks
- After block → short bullet explanation

5. ADAPTABILITY
- DO NOT hallucinate topics
- Follow input strictly
- Math → steps / formulas (NO long explanations)
- COA → flow, registers, tables

6. DEDUPLICATION
- If topic already explained → SKIP
- Do NOT restate same definition in different words

7. END MARKER
- Write EXACTLY once at the very end:
  ✅ Notes generated successfully
"""
def summarize_topic(topic: str, text: str) -> str:
    # SAFETY: prevent token overflow even if caller forgets
    MAX_INPUT_CHARS = 3500
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]




def summarize_topic(topic: str, text: str) -> str:
    user_prompt = f"""
Convert the following content into exam-ready notes.

IMPORTANT:
- Remove repeated statements if they appear multiple times
- For MATH-heavy content:
  • Prefer formulas / rules
  • Avoid verbose explanations
  • Avoid re-stating the same theorem

CONTENT:
{text}

Rules reminder:
- Prefer TABLES for comparisons/differences
- Avoid repetition
- Short but sufficient for exams
DOMAIN CONSTRAINT (VERY IMPORTANT):

- If content is MATHEMATICS / LOGIC:
  • DO NOT introduce electronics, circuits, COA, rectifiers, hardware
  • Stay strictly within given symbols, formulas, rules

- DO NOT add external topics not present in input

"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=MAX_TOKENS,
    )

    return response.choices[0].message.content.strip()
