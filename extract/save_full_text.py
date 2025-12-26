import os

OUTPUT_DIR = "output"
FULL_TEXT_PATH = os.path.join(OUTPUT_DIR, "full_text.txt")


def save_full_text(text, output_path=FULL_TEXT_PATH):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
