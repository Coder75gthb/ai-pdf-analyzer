import re

def format_exam_notes(text: str) -> str:
    lines = text.split("\n")
    out = []

    for line in lines:
        line = line.strip()

        # BIG HEADINGS
        if line.startswith("###"):
            title = line.replace("###", "").strip()
            out.append(
                f"\n<div style='font-size:24px;font-weight:800;text-decoration:underline;margin-top:18px'>{title}</div>\n"
            )
            continue

        # BULLETS
        if line.startswith("•"):
            out.append(
                f"<div style='font-size:18px;margin-left:18px'>• {line[1:].strip()}</div>"
            )
            continue

        # TABLE ROWS
        if "|" in line:
            out.append(line)
            continue

    return "\n".join(out)
