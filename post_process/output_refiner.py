def refine_pipeline_output(text: str) -> str:
    lines = text.split("\n")
    output = []
    inside_code = False

    for line in lines:
        line = line.rstrip()

        # BIG HEADINGS
        if line.startswith("###"):
            title = line.replace("###", "").strip()
            output.append(
                f"\n<div style='font-size:24px;font-weight:800;text-decoration:underline;margin-top:26px'>{title}</div>\n"
            )
            continue

        # CODE START
        if line.strip().lower() == "code":
            inside_code = True
            output.append(
                "<div style='background:#111;color:#00ffcc;padding:14px;border-radius:8px;font-family:monospace;font-size:16px;margin-top:10px'>"
            )
            continue

        # CODE END
        if inside_code and line.strip() == "":
            inside_code = False
            output.append("</div>")
            continue

        if inside_code:
            output.append(line.replace("<", "&lt;").replace(">", "&gt;") + "<br>")
            continue

        # EXPLANATION
        if line.lower().startswith("explanation"):
            output.append(
                "<div style='font-size:18px;font-weight:700;margin-top:10px'>Explanation:</div>"
            )
            continue

        # BULLETS
        if line.startswith("•"):
            output.append(
                f"<div style='font-size:18px;margin-left:20px'>{line}</div>"
            )
            continue

        # STEPS
        if line.startswith("→"):
            output.append(
                f"<div style='font-size:17px;margin-left:32px'>{line}</div>"
            )
            continue

        # TABLES
        if "|" in line:
            output.append(line)
            continue

    return "\n".join(output)
