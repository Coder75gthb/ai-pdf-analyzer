def format_table(rows):
    if not rows:
        return ""
    out = []
    for row in rows:
        if not row:
            continue
        clean = [str(c) for c in row if c is not None]
        if clean:
            out.append(" | ".join(clean))
    return "\n".join(out)
