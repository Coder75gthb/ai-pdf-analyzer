import streamlit as st
import tempfile
import os
import re

from pipeline import process_pdf_stream
from mcq_generator.mcq_llm import generate_mcqs

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from xml.sax.saxutils import escape

if "mcq_clicked" not in st.session_state:
    st.session_state.mcq_clicked = False



# ---------------- FONT SIZE ----------------
st.markdown(
    """
    <style>
    textarea {
        font-size: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- SESSION STATE ----------------
if "notes_text" not in st.session_state:
    st.session_state.notes_text = ""

if "mcqs_text" not in st.session_state:
    st.session_state.mcqs_text = None

if "notes_generated" not in st.session_state:
    st.session_state.notes_generated = False

# ---------------- BACKGROUND (UNCHANGED) ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        120deg,
        #0b1020,
        #0e1627,
        #0b1220
    );
    background-size: 200% 200%;
    animation: slowBG 40s ease infinite;
}
@keyframes slowBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- LAYOUT CSS (UNCHANGED) ----------------
st.markdown("""
<style>
.block-container {
    max-width: 1500px;
    padding-top: 2.5rem;
}
hr { display: none; }
.hero-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.hero-sub {
    text-align: center;
    opacity: 0.7;
    margin-bottom: 3rem;
}
.feature-card {
    background: #0e1117;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 1.8rem;
    margin-bottom: 1.8rem;
    margin-left: 80px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown('<div class="hero-title">AI PDF Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Exam-ready notes, clean PDFs, and MCQs</div>',
    unsafe_allow_html=True
)






# ---------------- LANDING VIEW ----------------
uploaded_pdf = None
generate_clicked = False

if not st.session_state.notes_generated:
    left, right = st.columns([4, 2], gap="large")

    with left:
        st.markdown("<h2>Upload PDF</h2>", unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        generate_clicked = st.button("Generate Notes", use_container_width=True)

    with right:
        st.markdown("""
        <div class="feature-card">
            <h4>Clean Exam Notes</h4>
            <p style="opacity:0.75">Structured, Revision friendly notes</p>
        </div>
        <div class="feature-card">
            <h4>PDF Generation</h4>
            <p style="opacity:0.75">Downloadable, well-formatted PDFs</p>
        </div>
        <div class="feature-card">
            <h4>MCQ Generator</h4>
            <p style="opacity:0.75">Conceptual exam-level MCQs</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- FILE HANDLING ----------------
pdf_path = None
if uploaded_pdf:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.getvalue())
        pdf_path = tmp.name

def dedupe_notes(text: str) -> str:
    seen = set()
    output = []
    for line in text.splitlines():
        key = re.sub(r"[^a-zA-Z0-9]", "", line).lower()
        if key and key not in seen:
            seen.add(key)
            output.append(line)
    return "\n".join(output)


def generate_pdf_bytes(notes_text: str):
    from io import BytesIO
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from xml.sax.saxutils import escape

    buffer = BytesIO()
    styles = getSampleStyleSheet()

    # ---------- CUSTOM STYLES ----------
    styles["Normal"].fontSize = 11
    styles["Normal"].leading = 14

    if "HeadingX" not in styles:
        styles.add(ParagraphStyle(
            name="HeadingX",
            fontSize=16,
            leading=20,
            spaceBefore=14,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        ))

    if "BulletX" not in styles:
        styles.add(ParagraphStyle(
            name="BulletX",
            fontSize=11,
            leading=14,
            leftIndent=18,
            spaceAfter=4,
        ))

    # ---------- DOC ----------
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    elements = []

    lines = notes_text.split("\n")
    table_buffer = []

    def flush_table():
        nonlocal table_buffer
        if not table_buffer:
            return

        col_count = max(len(row) for row in table_buffer)
        col_width = (A4[0] - 72) / col_count

        table = Table(
            table_buffer,
            colWidths=[col_width] * col_count,
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(Spacer(1, 10))
        elements.append(KeepTogether(table))
        elements.append(Spacer(1, 12))
        table_buffer = []

    for raw in lines:
        line = raw.strip()

        # REMOVE Cooking Notes completely
        if "Cooking Notes" in line:
            continue

        # REMOVE ** markers
        line = line.replace("**", "")

        # TABLE ROW
        if "|" in line and line.count("|") >= 2:
            cells = [Paragraph(escape(c.strip()), styles["Normal"])
                     for c in line.split("|") if c.strip()]
            table_buffer.append(cells)
            continue
        else:
            flush_table()

        # HEADING
        if line and line == line.title() and len(line.split()) <= 6:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(escape(line), styles["HeadingX"]))
            continue

        # BULLET
        if line.startswith("-") or line.startswith("•"):
            elements.append(Paragraph(
                escape(line.lstrip("-• ").strip()),
                styles["BulletX"]
            ))
            continue

        # NORMAL TEXT
        if line:
            elements.append(Paragraph(escape(line), styles["Normal"]))
        else:
            elements.append(Spacer(1, 8))

    flush_table()

    doc.build(elements)
    buffer.seek(0)
    return buffer



# ---------------- GENERATE NOTES ----------------
if uploaded_pdf and generate_clicked and not st.session_state.notes_generated:
    st.session_state.notes_text = ""
    st.session_state.mcqs_text = None

    container = st.empty()
    collected = []

    status = st.status("🍳 Cooking Notes...", expanded=True)

    for chunk in process_pdf_stream(pdf_path):
        collected.append(chunk)
        container.markdown("".join(collected), unsafe_allow_html=True)

    # final save
    st.session_state.notes_text = dedupe_notes("".join(collected))
    st.session_state.notes_generated = True

    #  THIS LINE DOES THE JOB
    status.update(label=" Notes generated successfully", state="complete")


# ---------------- DISPLAY ----------------
# if st.session_state.notes_text:
#     st.markdown("## Generated Notes")
#     st.markdown(st.session_state.notes_text)

    # ---- MCQ SECTION (STRICTLY GUARDED) ----
if st.session_state.get("notes_generated", False):

    st.markdown("## MCQ Generator")

    if st.button("Generate MCQs", key="mcq_btn"):
        with st.spinner("Generating MCQs..."):
            st.session_state.mcqs_text = generate_mcqs(
                st.session_state.notes_text[:4000],
                20
            )

if st.session_state.get("mcqs_text"):
    st.markdown("### MCQs")
    st.text(st.session_state.mcqs_text)

# ---------------- PDF DOWNLOAD ----------------
if st.session_state.notes_generated and st.session_state.notes_text:
    pdf_bytes = generate_pdf_bytes(st.session_state.notes_text)

    st.download_button(
        label="Download Notes as PDF",
        data=pdf_bytes,
        file_name="Exam_Notes.pdf",
        mime="application/pdf",
        use_container_width=True
    )
