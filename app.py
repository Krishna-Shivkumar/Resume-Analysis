import streamlit as st
import re
import ollama
import json
import spacy
from docx import Document
from PyPDF2 import PdfReader
from work_exp import work_experience, work_time
from jobposting import job_info

st.set_page_config(page_title="Resume Matcher", layout="wide")

# --- Utils ---
nlp = spacy.load("en_core_web_sm")
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    else:
        return ""
    
def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

def get_lemmas(text: str) -> str:
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(lemmas)

def calculate_match_score(resume_data, job_data):
 # Add back in later
 t = ''

# --- UI ---

st.markdown("## 📊 Bulk Resume Matcher")
st.markdown("Upload one job posting and 20–30 resumes. We'll rank each resume against the job.")

with st.form("upload_form"):
    job_file = st.file_uploader("💼 Upload Job Posting PDF", type="pdf", key="job")
    resume_files = st.file_uploader("📄 Upload 20–30 Resume PDFs", type="pdf", accept_multiple_files=True, key="resumes")
    submitted = st.form_submit_button("Analyze")

if submitted and job_file and resume_files:
    with st.spinner("🔍 Extracting job posting info..."):
        job_text = extract_text(job_file)
        job_data = extract_job_posting_info(job_text)

    match_results = []

    for file in resume_files:
        with st.spinner(f"📄 Processing {file.name}..."):
            resume_text = extract_text(file)
            try:
                resume_data = extract_resume_info(resume_text)
                score = calculate_match_score(resume_data, job_data)
                match_results.append({
                    "filename": file.name,
                    "score": score,
                    "resume_data": resume_data
                })
            except Exception as e:
                st.error(f"❌ Failed to parse {file.name}: {e}")

    if match_results:
        st.success(f"✅ Processed {len(match_results)} resumes successfully.")

        sorted_results = sorted(match_results, key=lambda x: x["score"], reverse=True)

        st.markdown("### 🏆 Ranked Results")
        for i, res in enumerate(sorted_results):
            with st.expander(f"#{i+1}: {res['filename']} — Score: {res['score']}/100", expanded=i==0):
                st.markdown(f"**Education:** {res['resume_data'].get('education_level', 'N/A')}")
                st.markdown(f"**Experience:** {res['resume_data'].get('experience_summary', 'N/A')}")
                st.markdown(f"**Skills:** {', '.join(res['resume_data'].get('skills', []))}")

    else:
        st.warning("⚠ No successful resumes parsed.")


