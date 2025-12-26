from pipeline import process_pdf
from summarize_all_chunks import summarize_all_chunks

# 1. PDF → chunks
chunks = process_pdf("sample.pdf")  # ya jo bhi test pdf hai

print("Total chunks:", len(chunks))

# 2. Only first 3 chunks summarize (CPU heavy hota hai)
summaries = summarize_all_chunks(chunks[:3])

# 3. Print results
for item in summaries:
    print("\n====================")
    print("TITLE:", item["title"])
    print("SUMMARY:")
    print(item["summary"])

import json

with open("output/summaries.json", "w", encoding="utf-8") as f:
    json.dump(summaries, f, indent=2, ensure_ascii=False)

print("Summaries saved.")
