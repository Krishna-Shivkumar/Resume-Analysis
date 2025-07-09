import streamlit as st
import re
import spacy
from io import BytesIO
from docx import Document as DocxDocument
from PyPDF2 import PdfReader
from google.cloud import documentai_v1 as documentai
from fpdf import FPDF
import unicodedata

from work_exp import work_experience, work_time
from jobposting import job_info
from skills_and_education import resume_skill, extract_highest_education, extract_major

st.set_page_config(page_title="Resume Matcher", layout="wide")

# --- Google Document AI Config ---
PROJECT_ID = "resume-465414"
LOCATION = "us"
PROCESSOR_ID = "4da0edcaa19b9f53"

# --- Load Spacy model once ---
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    # Normalize unicode to ASCII, e.g., convert “–” to “-”
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

def docx_to_pdf_bytes(docx_file) -> bytes:
    """
    Convert a docx file-like object to PDF bytes in-memory
    by extracting text, cleaning unicode chars, and writing with fpdf.
    """
    doc = DocxDocument(docx_file)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            cleaned = clean_text(text)
            pdf.multi_cell(0, 10, cleaned)

    pdf_bytes = pdf.output(dest='S').encode('latin1')  # output PDF as string, encode to bytes
    return pdf_bytes

def parse_document_bytes(file_bytes: bytes, mime_type: str) -> str:
    """Parse document bytes using Google Document AI and return extracted text."""
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"
    raw_document = documentai.RawDocument(content=file_bytes, mime_type=mime_type)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    try:
        result = client.process_document(request=request)
        document = result.document
        return document.text
    except Exception as e:
        st.error(f"Error processing document with Document AI: {e}")
        return ""

def normalize_text(text: str) -> str:
    """Lowercase and remove special characters except spaces."""
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

def get_lemmas(text: str) -> str:
    """Lemmatize text and remove stopwords."""
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(lemmas)

def extract_email(text: str) -> str:
    """Extract first email from text or return 'Not found'."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not found"

# --- UI ---

st.markdown("## 📊 Bulk Resume Matcher")
st.markdown("Upload one job posting and 20–30 resumes. We'll rank each resume against the job.")

with st.form("upload_form"):
    job_file = st.file_uploader("💼 Upload Job Posting PDF or DOCX", type=["pdf", "docx"], key="job")
    resume_files = st.file_uploader("📄 Upload 20–30 Resumes PDFs or DOCXs", type=["pdf", "docx"], accept_multiple_files=True, key="resumes")
    submitted = st.form_submit_button("Analyze")

if submitted and job_file and resume_files:
    with st.spinner("🔍 Extracting job posting info with Document AI..."):
        if job_file.name.lower().endswith(".docx"):
            pdf_bytes = docx_to_pdf_bytes(job_file)
            job_text = parse_document_bytes(pdf_bytes, "application/pdf")
        else:
            job_bytes = job_file.read()
            job_text = parse_document_bytes(job_bytes, "application/pdf")

        if not job_text:
            st.error("Failed to parse job posting. Please try again.")
            st.stop()

        job_text = normalize_text(job_text)
        job_text = get_lemmas(job_text)
        j_info = job_info(job_text)

    results = {}
    total = len(resume_files)
    progress_bar = st.progress(0)
    EDUCATION_LEVELS = {"high school": 1, "associate": 2, "bachelor": 3, "master": 4, "phd": 5}
    job_edu = 0
    for e in EDUCATION_LEVELS.keys():
        if e in j_info.get('education_level', ''):
            job_edu = EDUCATION_LEVELS[e]

    for i, resume_file in enumerate(resume_files):
        with st.spinner(f"Processing resume {i+1}/{total} ({resume_file.name})..."):
            if resume_file.name.lower().endswith(".docx"):
                pdf_bytes = docx_to_pdf_bytes(resume_file)
                resume_text = parse_document_bytes(pdf_bytes, "application/pdf")
            else:
                resume_bytes = resume_file.read()
                resume_text = parse_document_bytes(resume_bytes, "application/pdf")

            if not resume_text:
                st.warning(f"Skipping {resume_file.name} due to parsing error.")
                progress_bar.progress((i + 1) / total)
                continue

            resume_text = normalize_text(resume_text)
            resume_text = get_lemmas(resume_text)

            # Scoring
            score, notskills = resume_skill(j_info["skills"], resume_text)
            education = extract_highest_education(resume_text)
            major = extract_major(resume_text)
            work_duration = work_time(resume_text)
            temp = 0
            problems = ""

            for e in EDUCATION_LEVELS.keys():
                if e in education:
                    temp = EDUCATION_LEVELS[e]

            if temp >= job_edu:
                score += 100 / 3
            else:
                problems += f"User does not have the required education level. User has a <{education}> level education.\n"

            if work_duration >= int(j_info.get("required_experience_time", 0)):
                score += 100 / 3
            elif work_duration >= 0:
                score += 100 * (work_duration / int(j_info.get("required_experience_time", 1)))
                problems += f"User does not have the required experience. User has {work_duration} years of experience.\n"
            else:
                problems += "Error evaluating work experience duration.\n"

            if len(notskills) > 0:
                problems += "Missing Skills: " + ", ".join(notskills) + "\n"

            email = extract_email(resume_text)
            results[email] = [score, problems]

        progress_bar.progress((i + 1) / total)

    sorted_results = sorted(results.items(), key=lambda item: item[1][0], reverse=True)

    st.markdown("## 🧾 Final Ranking:")
    for email, (score, problems) in sorted_results:
        st.markdown(f"### 📧 {email}")
        st.write(f"**Score:** {round(score, 2)}")
        st.write(f"**Issues:**\n{problems if problems else 'None'}")
        st.divider()

    st.success("✅ All resumes have been processed.")
