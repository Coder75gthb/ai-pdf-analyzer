def refine_pipeline_output(raw_output: str) -> str:
    lines = raw_output.splitlines()
    cleaned = []
    seen = set()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Kill OCR garbage lines
        if len(line) > 120 and line.count("|") > 20:
            continue

        if line in seen:
            continue

        seen.add(line)
        cleaned.append(line)

    final = "\n".join(cleaned)

    if not final.startswith("📌 SUMMARY NOTES"):
        final = "📌 SUMMARY NOTES\n\n" + final

    return final
