from pipeline import process_pdf

PDF_PATH = "sample.pdf"

def run():
    print("\n🚀 Starting AI PDF Analyzer...\n")

    try:
        results = process_pdf(PDF_PATH)
    except Exception as e:
        print("❌ Pipeline crashed:")
        print(e)
        return

    for idx, item in enumerate(results, start=1):
        print("\n" + "=" * 100)
        print(f"📌 TOPIC {idx}: {item['topic']}")
        print("=" * 100)
        print(item["notes"])

    print("\n✅ Done.\n")

if __name__ == "__main__":
    run()
