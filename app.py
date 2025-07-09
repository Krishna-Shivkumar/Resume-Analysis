import streamlit as st
import re
import ollama
import json
import spacy
import unicodedata
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

def clean_text(text: str) -> str:
    """Normalize and clean extracted text from PDF or DOCX."""
    text = unicodedata.normalize("NFKD", text)      # Normalize Unicode (e.g., weird quotes/spaces)
    text = text.replace('\xa0', ' ')                # Replace non-breaking spaces
    text = text.replace('\n', ' ').replace('\r', '')  # Remove newlines
    text = re.sub(r'\s+', ' ', text)                # Collapse multiple spaces
    return text.strip()

def extract_email(text: str) -> str:
    """Extract the first email address found in the text."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not found"

def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s@.+\-_/()]", " ", text.lower())

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
    job_file = st.file_uploader("💼 Upload Job Posting PDF", type=["pdf","docx"], key="job")
    resume_files = st.file_uploader("📄 Upload 20–30 Resume PDFs", type=["pdf","docx"], accept_multiple_files=True, key="resumes")
    submitted = st.form_submit_button("Analyze")

if submitted and job_file and resume_files:
    with st.spinner("🔍 Extracting job posting info..."):
        job_text = extract_text(job_file)
        # job_text = clean_text(job_text)
        job_text= normalize_text (job_text)
        # job_text= get_lemmas (job_text)
        j_info=job_info(job_text)

        results = {}
    placeholder = st.empty()  # For dynamic updates
    progress_bar = st.progress(0)

    total = len(resume_files)
    EDUCATION_LEVELS = {"high school":1, "associate":2, "bachelor":3, "master":4, "phd":5}
    job_edu = 0
    print(job_edu)
    for e in EDUCATION_LEVELS.keys():
            if e in j_info['education_level']:
                job_edu = EDUCATION_LEVELS[e]
    with st.spinner("🔍 Processing Resumes..."):
        for i, resume_file in enumerate(resume_files):
            resume_text = extract_text(resume_file)
            # resume_text = clean_text(resume_text)
            resume_text = normalize_text(resume_text)
            # resume_text = get_lemmas(resume_text)
            # print(resume_text)

            # You can extract fields using your external functions here
            score, notskills = resume_skill (j_info["skills"],resume_text)
            education = extract_highest_education(resume_text)
            print(education)
            major = extract_major(resume_text)
            resume_exp = work_experience(resume_text, j_info['required_experience_field'])
            work_duration = work_time(resume_exp)
            temp = 0
            problems = ""
            for e in EDUCATION_LEVELS.keys():
                if e in education:
                    temp = EDUCATION_LEVELS[e]
            if(temp>=job_edu):
                score+=100/3
            else:
                problems+="User does not have the required education level.  User has a <"+education+"> level education.\n"
            try:
                if(j_info["required_experience_time"] is None):
                    j_info["required_experience_time"] = 0
                if(work_duration >= float(j_info["required_experience_time"])):
                    score+=100/3
                elif(work_duration >=0):
                    score+= 100*(work_duration/float(j_info["required_experience_time"]))/3
                    problems+="User does not have the required experience.  User has "+str({round(work_duration, 2)})+" years of experience.\n"
                else:
                    raise ValueError("There has been an error evaluating a resume.  Please resubmit and try again.")
            except TypeError:
                raise ValueError("The Job description does not clearly state how much experience is preferred.  Please resubmit a more specific job description.")
            if len(notskills)>0: problems+='Missing Skills: '
            for s in notskills:
                problems+=s+', '
            email=extract_email(resume_text)
            results[email] = [score, problems]
            sorted_results = sorted(results.items(), key=lambda item: item[1][0], reverse=True)

            # Sort and display partial results
            # sorted_results = sorted(results.items(), key=lambda item: item[1][0], reverse=True)
            with placeholder.container():
                st.markdown("## 🧾 Current Ranking:")
                for email, (score, problems) in sorted_results:
                    st.markdown(f"### 📧 {email}")
                    st.write(f"**Score:** {round(score, 2)}")
                    st.write(f"**Issues:**\n{problems if problems else 'None'}")
                    st.divider()
            # Update progress bar
            progress_bar.progress((i + 1) / total)

    st.success("✅ All resumes have been processed.")


