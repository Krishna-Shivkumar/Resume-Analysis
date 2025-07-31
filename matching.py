import json
import ollama
import os
from google import genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

load_dotenv()
api_k = os.getenv("API_KEY")
# try:
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "intern-api-use.json"
# except:
#     print("Key Not Found")
client = genai.Client(
    api_key=api_k
)


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
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= prompt,
    )
    return response.text

def calculate_match_score(resume_data, job_data):
    # Score: out of 100
    score = 0

    # Education match (20 points)
    edu_levels = ["High School", "Associate's", "Bachelor's", "Master's", "PhD"]
    try:
        resume_edu = resume_data['education_level']
        job_edu = job_data['education_level']
        if resume_edu in edu_levels and job_edu in edu_levels:
            if edu_levels.index(resume_edu) >= edu_levels.index(job_edu):
                score += 20
    except:
        pass

    # Experience match (30 points, simple keyword match)
    try:
        resume_exp = resume_data['experience_summary'].lower()
        job_exp = job_data['required_experience'].lower()
        if any(keyword in resume_exp for keyword in job_exp.split()):
            score += 20
        if any(num in resume_exp for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
            score += 10
    except:
        pass

    # Skills match (50 points)
    try:
        resume_skills = set(s.lower() for s in resume_data['skills'])
        job_skills = set(s.lower() for s in job_data['skills'])
        overlap = resume_skills.intersection(job_skills)
        match_ratio = len(overlap) / len(job_skills) if job_skills else 0
        score += round(match_ratio * 50)
    except:
        pass

    return score

### === Main Logic ===

print("Reading resume and job posting...")

resume_text = extract_text_from_pdf("resume.pdf")
job_text = extract_text_from_pdf("job_posting.pdf")

print("Extracting resume information...")
resume_data = extract_resume_info(resume_text)
print(json.dumps(resume_data, indent=2))

print("\nExtracting job posting information...")
job_data = extract_job_posting_info(job_text)
print(json.dumps(job_data, indent=2))

print("\nCalculating match score...")
score = calculate_match_score(resume_data, job_data)
print(f"\n🎯 Match Score: {score}/100")

if score > 80:
    print("✅ Strong match!")
elif score > 50:
    print("🟡 Moderate match. Consider tweaking your resume.")
else:
    print("🔴 Weak match. May need to improve alignment.")
