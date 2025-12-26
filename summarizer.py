# llm/groq_summarizer.py

from groq import Groq

client = Groq(api_key="YOUR_API_KEY_HERE")

MAX_CHARS = 2600
MAX_TOKENS = 400


def split_text(text):
    return [text[i:i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]


def summarize_topic(topic, text):
    raw_blocks = []

    for chunk in split_text(text):
        prompt = f"""
You are extracting RAW EXAM POINTS.

STRICT RULES:
- Bullet points ONLY
- Max 5 bullets per concept
- Each bullet ≤ 12 words
- NO explanations
- NO paragraphs
- NO repetition
- NO examples unless formula-like

OUTPUT FORMAT ONLY:

## HEADING
• point
• point

CONTENT:
{chunk}
"""
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=MAX_TOKENS
        )

        raw_blocks.append(res.choices[0].message.content.strip())

    # 🔥 SECOND PASS — BRUTAL COMPRESSOR
    compressor_prompt = f"""
You are converting RAW POINTS into FINAL EXAM NOTES.

ABSOLUTE RULES:
- Keep ONLY exam-relevant points
- Remove ALL repetition
- Max 4 bullets per heading
- Convert comparisons into TABLES
- RISC vs CISC → TABLE
- Big vs Little Endian → TABLE
- NO paragraphs
- NO filler words

FORMAT:

### __HEADING__
• bullet
• bullet

TABLE FORMAT:
| Feature | A | B |

RAW NOTES:
{chr(10).join(raw_blocks)}
"""

    final = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": compressor_prompt}],
        temperature=0.0,
        max_tokens=700
    )

    return final.choices[0].message.content.strip()
