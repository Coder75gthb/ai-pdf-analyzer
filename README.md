# AI PDF Analyzer 

An AI-powered Streamlit application that converts PDFs into **exam-ready notes and MCQs**, with detailing into most of the concepts.

This project focuses on producing **clean, usable study material** instead of verbose or hallucinated summaries.

---

## What This Project Does

- Converts PDFs into concise, exam-focused notes
- Generates MCQs from extracted content
- Uses **separate processing pipelines** for:
  -  General (non-math) PDFs
  -  Math-heavy PDFs
- Designed to work on **real, messy academic PDFs**

---

## Why Math PDFs Are Treated Differently

Math PDFs are one of the hardest inputs for LLMs because they contain:
- proofs and derivations mixed with theory
- examples and solved problems inline
- repeated restatements of the same result
- symbolic noise that looks like formulas but isn’t


 Math-heavy PDFs are processed conservatively, with output quality influenced by the structure and formatting of the source document.
 This is an **intentional design decision** to reduce hallucinations.

---

##  Key Features

- Clean, structured exam notes
- Dedicated math summarization pipeline
- Aggressive filtering to remove noise from math content
- MCQ generation from extracted notes
- Streamlit-based interactive interface
- Modular and extensible codebase
  

---

##  Tech Stack

- **Python**
- **Streamlit**
- **Groq LLM (LLaMA 3.1)**
- Regex-based content sanitization
- Modular processing pipeline

---

##  How to Run Locally

```bash
# Step 1: Clone the repository
git clone https://github.com/<your-username>/ai-pdf-analyzer.git
cd ai-pdf-analyzer

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Set Groq API key (Windows)
set GROQ_API_KEY=your_api_key_here

# Step 4: Run the Streamlit app
streamlit run app.py 
