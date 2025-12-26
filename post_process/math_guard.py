import re

def protect_math(text: str) -> str:
    # Wrap register transfers & expressions
    patterns = [
        r'[A-Z]+\[\d+(?::\d+)?\]\s*[←→=]\s*[A-Z]+\[\d+(?::\d+)?\]',
        r'[≤≥≠∧∨¬⊕→←]'
    ]

    for p in patterns:
        text = re.sub(p, lambda m: f"`{m.group(0)}`", text)

    return text
