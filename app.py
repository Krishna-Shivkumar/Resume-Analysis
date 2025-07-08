import streamlit as st
import re
import ollama
import json
import spacy
from docx import Document
from PyPDF2 import PdfReader
from work_exp import work_experience, work_time
from jobposting import job_info
from skills_and_education import resume_skill, extract_highest_education, extract_major

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
        job_text= normalize_text (job_text)
        job_text= get_lemmas (job_text)
        j_info=job_info(job_text)

        results = {}
    placeholder = st.empty()  # For dynamic updates
    progress_bar = st.progress(0)

    total = len(resume_files)
    for i, resume_file in enumerate(resume_files):
        resume_text = extract_text(resume_file)
        resume_text = normalize_text(resume_text)
        resume_text = get_lemmas(resume_text)

        # You can extract fields using your external functions here
        prop, notskills = resume_skill (j_info["skills"],resume_text)
        education = extract_highest_education(resume_text)
        major = extract_major(resume_text)
        work_duration = work_time(resume_text)
        if (education in j_info ["education_level"]):
            prop+=100/3
        results.append({
            "File Name": resume_file.name,
            "Score": round(score, 2),
            "Skills": skills,
            "Education": education,
            "Major": major,
            "Experience (yrs)": work_duration
        })

        # Sort and display partial results
        sorted_results = sorted(results, key=lambda x: x["Score"], reverse=True)
        placeholder.dataframe(sorted_results)  # or placeholder.table(sorted_results)

        # Update progress bar
        progress_bar.progress((i + 1) / total)

    st.success("✅ All resumes have been processed.")


