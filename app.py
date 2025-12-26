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


# ---------------- SESSION STATE ----------------
if "notes_text" not in st.session_state:
    st.session_state.notes_text = ""

if "mcqs_text" not in st.session_state:
    st.session_state.mcqs_text = None

if "notes_generated" not in st.session_state:
    st.session_state.notes_generated = False



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





st.markdown("""
<style>
.block-container {
    max-width: 1500px;
    padding-top: 2.5rem;
}

/* remove weird invisible gaps */
div[data-testid="stFileUploader"] > section {
    padding-top: 0 !important;
    margin-top: 0 !important;
}


/* remove hr */
hr { display: none; }

/* hero */
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

/* Upload card */
.upload-card {
    background: #0e1117;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 2.8rem;
}

/* Feature cards */
.feature-card {
    background: #0e1117;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 1.8rem;
    margin-bottom: 1.8rem;
    margin-left: 80px;
    transition: all 0.3s ease;
}

.feature-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 24px rgba(59,130,246,0.28);
    transform: translateY(-4px);
}

.feature-card h4 {
    margin-bottom: 0.4rem;
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
    label_visibility="collapsed"
    # LEFT MUCH BIGGER, RIGHT PUSHED
    left, right = st.columns([4, 2], gap="large")

    

    with left:
        

        st.markdown("<h2>Upload PDF</h2>", unsafe_allow_html=True)

        
        uploaded_pdf = st.file_uploader(
            "",
            type=["pdf"],
            label_visibility="collapsed"
        )



       
        generate_clicked = st.button(
            "Generate Notes",
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="feature-card">
            <h4>Clean Exam Notes</h4>
            <p style="opacity:0.75">
            Structured, Revision friendly notes
            </p>
        </div>

        <div class="feature-card">
            <h4>PDF Generation</h4>
            <p style="opacity:0.75">
            Downloadable, well-formatted PDFs
            </p>
        </div>

        <div class="feature-card">
            <h4>MCQ Generator</h4>
            <p style="opacity:0.75">
            Conceptual exam-level MCQs
            </p>
        </div>
        """, unsafe_allow_html=True)


# ---------------- FILE HANDLING ----------------
if uploaded_pdf:
    st.session_state.notes_generated = False
    st.session_state.notes_text = ""
    st.session_state.mcqs_text = None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        pdf_path = tmp.name


# ---------------- DEDUPE ----------------
def dedupe_notes(text: str) -> str:
    seen = set()
    output = []

    for line in text.split("\n"):
        key = line.strip().lower()
        if not key:
            output.append(line)
            continue
        if key in seen:
            continue
        seen.add(key)
        output.append(line)

    return "\n".join(output)


# ---------------- PDF GENERATION ----------------
def generate_pdf_from_notes(text: str, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    elements = []
    bullet_buffer = []
    table_buffer = []
    usable_width = doc.width

    def clean_text(s: str) -> str:
        s = s.replace("**", "")
        s = re.sub(r"^_+(.*?)_+$", r"\1", s)
        s = s.lstrip("> ").strip()
        return escape(s)

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            elements.append(
                ListFlowable(
                    [ListItem(Paragraph(clean_text(b), normal_style)) for b in bullet_buffer],
                    bulletType="bullet",
                    leftIndent=20
                )
            )
            bullet_buffer = []

    def flush_table():
        nonlocal table_buffer
        if not table_buffer:
            return

        filtered = []
        for row in table_buffer:
            cells = row.split("|")[1:-1]
            if all(cell.strip().startswith("-") for cell in cells):
                continue
            if not any(cell.strip() for cell in cells):
                continue
            filtered.append([cell.strip() for cell in cells])

        if len(filtered) < 2:
            table_buffer = []
            return

        if filtered[0] and filtered[0][0] == "":
            filtered = [row[1:] for row in filtered]

        col_widths = [usable_width / len(filtered[0])] * len(filtered[0])
        data = [[Paragraph(clean_text(c), normal_style) for c in row] for row in filtered]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 14))
        table_buffer = []

    for line in text.split("\n"):
        line = line.rstrip()

        if re.match(r"^\s*-{3,}\s*$", line):
            continue
        if re.match(r"^\s*\|?\s*-+\s*\|.*", line):
            continue

        if line.startswith("•"):
            flush_table()
            bullet_buffer.append(line[1:].strip())

        elif line.startswith("|") and "|" in line[1:]:
            flush_bullets()
            table_buffer.append(line)

        elif not line.strip():
            flush_bullets()
            flush_table()
            elements.append(Spacer(1, 10))

        else:
            flush_bullets()
            flush_table()
            elements.append(Paragraph(clean_text(line), normal_style))

    flush_bullets()
    flush_table()
    doc.build(elements)


# ---------------- SANITIZE ----------------
def sanitize_text_for_pdf(text: str) -> str:
    cleaned = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            cleaned.append("")
            continue
        if "cooking notes" in line.lower():
            continue
        if re.fullmatch(r"-{3,}", line):
            continue
        line = re.sub(r"^\*\s*", "• ", line)
        line = line.replace("**", "").replace("_", "")
        cleaned.append(line)
    return "\n".join(cleaned)


# ---------------- GENERATE NOTES ----------------
if uploaded_pdf and generate_clicked:
    if st.session_state.notes_generated:
        st.warning("Notes already generated for this PDF.")
    else:
        collected_chunks = []
        for chunk in process_pdf_stream(pdf_path):
            st.markdown(chunk)
            collected_chunks.append(chunk)

        st.session_state.notes_text = dedupe_notes("\n".join(collected_chunks))
        st.session_state.notes_generated = True
        st.success("Notes generated successfully")


# ---------------- NOTES + PDF ----------------
if st.session_state.notes_text:
    st.markdown("## Generated Notes")
    st.markdown(st.session_state.notes_text)

    pdf_path = os.path.join(tempfile.gettempdir(), "AI_PDF_Analyzer_Notes.pdf")
    generate_pdf_from_notes(
        sanitize_text_for_pdf(st.session_state.notes_text),
        pdf_path
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            "Download Notes as PDF",
            f,
            file_name="AI_PDF_Analyzer_Notes.pdf",
            mime="application/pdf"
        )

    st.markdown("## MCQ Generator")

    if st.button("Generate MCQs"):
        with st.spinner("Generating MCQs"):
            try:
                st.session_state.mcqs_text = generate_mcqs(
                    st.session_state.notes_text[:4000],
                    num_questions=20
                )
            except Exception:
                st.session_state.mcqs_text = "MCQ generation failed."


# ---------------- MCQ OUTPUT ----------------
if st.session_state.mcqs_text:
    st.markdown("### MCQs")
    st.text(st.session_state.mcqs_text)
