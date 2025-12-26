import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

client = Groq(api_key=GROQ_API_KEY)


def generate_mcqs(text: str, num_questions: int = 25) -> str:
    prompt = f"""
Generate {num_questions} HIGH-QUALITY exam MCQs.

STRICT RULES:
- Conceptual, exam-oriented questions
- Avoid definition-only questions
- 4 options (A–D)
- Exactly ONE correct answer
- NO explanations
- Clean readable format
- No emojis

FORMAT:

Q1. Question?
A) ...
B) ...
C) ...
D) ...

Answer: B

CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You generate exam-level MCQs."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1200,
    )

    return response.choices[0].message.content.strip()
