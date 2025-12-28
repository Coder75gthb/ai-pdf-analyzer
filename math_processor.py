import re
from llm.groq_summarizer import client, MODEL, MAX_TOKENS

MATH_SYSTEM_PROMPT = """
You are a Technical Note Taker. 

TASKS:
1. Extract all formulas, theorems, and definitions.
2. If no clear formulas exist, summarize the key technical concepts in 2-3 concise bullets.
3. Use $...$ for all mathematical symbols so they render clearly.

STRICT SILENCE:
- DO NOT mention "LaTeX", "formatting", or "Markdown".
- DO NOT say "No relevant content found". If content is thin, just summarize what is there.
- NEVER explain what you are doing. Just provide the notes.
"""
def summarize_math_chunk(text: str) -> str:
    user_prompt = f"EXTRACT FORMULAS ONLY FROM THIS TEXT. IGNORE EXAMPLES:\n\n{text}"
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": MATH_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0, # Forces logic over creativity
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content