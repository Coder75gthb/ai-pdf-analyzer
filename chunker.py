def chunk_text(text, max_words=800):
    """
    Splits text into chunks of approximately max_words words.
    Returns a list of chunk strings.
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = words[i:i + max_words]
        chunk_text = " ".join(chunk)
        chunks.append(chunk_text)

    return chunks
