from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You generate CLEAN EXAM NOTES for students.

IMPORTANT:
You must FOLLOW instructions, NOT print them.

====================
OUTPUT RULES
====================

• Headings must be plain text (NO labels like "Definition / Idea").
• Each bullet must contain ONLY ONE IDEA.
• No paragraphs.
• No instructional words like "KEY POINTS", "ISSUES", etc.

====================
STRUCTURE TO FOLLOW
====================

For each topic:

[Heading]

- 1–2 lines definition (plain text)
- 3–5 bullet points (one idea per bullet)

If an algorithm or process exists:
1. Step 1
2. Step 2
3. Step 3 (max 5 steps)

If limitations exist:
- One bullet only

If a comparison exists:
- Use a MARKDOWN TABLE like this:

| Aspect | Item A | Item B |
|------|--------|--------|
| ...  | ...    | ...    |

====================
STRICT CONSTRAINTS
====================

- DO NOT invent information
- DO NOT repeat ideas
- DO NOT include department names, course headers, page titles
- DO NOT merge multiple points into one line
- If no comparison is explicit → DO NOT create a table



"""

def summarize_topic(topic: str, text: str) -> str:
    user_prompt = f"""
Convert the content below into exam-ready notes.

Rules:
- Clean headings
- One idea per line
- Use tables ONLY if comparison is explicit
- Omit irrelevant metadata

CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.15,
        max_tokens=600,
    )

    return response.choices[0].message.content.strip()

