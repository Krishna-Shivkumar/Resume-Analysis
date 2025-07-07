import json
import ollama
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

print('reached1')
job_posting_text = extract_text_from_pdf('job_posting.pdf')  # Change filename as needed
print('reached2')

prompt = f"""
You are an AI assistant designed to extract structured data from job postings.

From the job description below, extract the following:
1. The highest required level of education (e.g. High School, Bachelor's Degree, Master's Degree, PhD).
2. The type of experience required (e.g. 3+ years in software engineering, prior experience in customer service, etc).
3. A list of relevant skills (e.g. Python, project management, communication, etc).

Return the output as a JSON object with the following structure:
{{
  "education_level": "<highest level of education>",
  "required_experience": "<summary of experience needed>",
  "skills": ["<skill1>", "<skill2>", ...]
}}

Job Description:
\"\"\"
{job_posting_text}
\"\"\"
"""

print('reached3')

response = ollama.generate(
    model="mistral:7b",
    prompt=prompt,
    stream=False
)

result = response['response']
print("\n=== Raw LLM Response ===\n")
print(result)

try:
    job_data = json.loads(result)
    print("\n=== Parsed Job Posting JSON ===\n")
    print(json.dumps(job_data, indent=2))
except Exception as e:
    print("\nWarning: Could not parse as JSON.")
    print(e)
