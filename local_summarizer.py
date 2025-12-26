from transformers import pipeline

# load local summarization model (FREE, offline)
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1  # CPU
)

MAX_INPUT_CHARS = 3000  # IMPORTANT: prevents index out of range


def summarize_chunk(title: str, content: str) -> str:
    """
    Safely summarize a single chunk using local model
    """

    if not content.strip():
        return ""

    # truncate content to safe length
    safe_text = content[:MAX_INPUT_CHARS]

    result = summarizer(
        safe_text,
        max_length=180,
        min_length=80,
        do_sample=False
    )

    return result[0]["summary_text"]
