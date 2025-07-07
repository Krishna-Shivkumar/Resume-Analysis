import streamlit as st
import ollama
import json
from PyPDF2 import PdfReader

st.set_page_config(page_title="Resume Matcher", layout="wide")

# --- Utils ---

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_resume_info(resume_text):
    prompt = f"""
From the resume below, extract the following:
1. Highest level of education (e.g. High School, Bachelor's, Master's, PhD)
2. Total years of work experience and a brief summary
3. A list of relevant skills

Return the output as a JSON object with keys: education_level, experience_summary, skills.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""
    response = ollama.generate(model="mistral:7b", prompt=prompt, stream=False)
    return json.loads(response['response'])

def extract_job_posting_info(job_text):
    prompt = f"""
From the job posting below, extract the following:
1. Highest required level of education
2. Required experience (years and type)
3. A list of required or preferred skills

Return the output as a JSON object with keys: education_level, required_experience, skills.

Job Posting:
\"\"\"
{job_text}
\"\"\"
"""
    response = ollama.generate(model="mistral:7b", prompt=prompt, stream=False)
    return json.loads(response['response'])

def calculate_match_score(resume_data, job_data):
    score = 0
    edu_levels = ["High School", "Associate's", "Bachelor's", "Master's", "PhD"]

    # Education
    try:
        r_edu = resume_data['education_level']
        j_edu = job_data['education_level']
        if r_edu in edu_levels and j_edu in edu_levels:
            if edu_levels.index(r_edu) >= edu_levels.index(j_edu):
                score += 20
    except: pass

    # Experience
    try:
        r_exp = resume_data['experience_summary'].lower()
        j_exp = job_data['required_experience'].lower()
        if any(keyword in r_exp for keyword in j_exp.split()):
            score += 20
        if any(num in r_exp for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
            score += 10
    except: pass

    # Skills
    try:
        r_skills = set(s.lower() for s in resume_data['skills'])
        j_skills = set(s.lower() for s in job_data['skills'])
        overlap = r_skills.intersection(j_skills)
        match_ratio = len(overlap) / len(j_skills) if j_skills else 0
        score += round(match_ratio * 50)
    except: pass

    return score

# --- UI ---

st.markdown("## 📊 Bulk Resume Matcher")
st.markdown("Upload one job posting and 20–30 resumes. We'll rank each resume against the job.")

with st.form("upload_form"):
    job_file = st.file_uploader("💼 Upload Job Posting PDF", type="pdf", key="job")
    resume_files = st.file_uploader("📄 Upload 20–30 Resume PDFs", type="pdf", accept_multiple_files=True, key="resumes")
    submitted = st.form_submit_button("Analyze")

if submitted and job_file and resume_files:
    with st.spinner("🔍 Extracting job posting info..."):
        job_text = extract_text_from_pdf(job_file)
        job_data = extract_job_posting_info(job_text)

    match_results = []

    for file in resume_files:
        with st.spinner(f"📄 Processing {file.name}..."):
            resume_text = extract_text_from_pdf(file)
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


