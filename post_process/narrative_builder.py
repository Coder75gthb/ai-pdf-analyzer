import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Reprint\s+\d{4}-\d{2}.*?\d+', '', text)
    text = re.sub(r'Department of.*?\d+', '', text)
    return text.strip()


def split_into_topics(text: str):
    """
    Very conservative topic splitter.
    Prevents random headings like 0 1 2 3.
    """
    lines = text.split("\n")
    topics = []
    current = {"title": "Overview", "content": []}

    for line in lines:
        line = line.strip()

        if len(line) < 4:
            continue

        # Heading heuristic (ALL CAPS or ends with :)
        if (
            line.isupper()
            or line.endswith(":")
            or re.match(r'^[A-Z][A-Za-z\s]{4,}$', line)
        ):
            if current["content"]:
                topics.append(current)
            current = {"title": line[:80], "content": []}
        else:
            current["content"].append(line)

    if current["content"]:
        topics.append(current)

    return topics
