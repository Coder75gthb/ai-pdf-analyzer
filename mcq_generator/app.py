import streamlit as st
from pipeline import process_pdf_stream

st.set_page_config(layout="wide")

st.markdown(
    "<h1 style='font-size:42px;'>AI PDF Analyzer</h1>",
    unsafe_allow_html=True
)

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded:
    st.markdown("###")  # spacing
    generate = st.button("Analyze / Generate Notes")

    if generate:
        st.markdown("🧠 Cooking notes... 🔍")

        # TEMP: assume chunks already extracted & cleaned
        # Replace this with your real extractor
        dummy_chunks = [
            "Operators include arithmetic, comparison and logical operators.",
            "Arithmetic operators include addition, subtraction, multiplication."
        ]

        output_box = st.empty()

        full_output = ""

        for chunk in process_pdf_stream(dummy_chunks):
            full_output += chunk + "\n\n"
            output_box.markdown(full_output)
