import json
import ollama
import re
from PyPDF2 import PdfReader

def job_info(job_posting_text):
    prompt = f"""
    From the job description below, extract the following:
    1. The highest required level of education (e.g. High School, Bachelor's Degree, Master's Degree, PhD).
    2. The type of experience required (e.g. software engineering, prior experience in customer service, etc).
    3. The amount of time spent in the 
    4. A list of relevant skills (e.g. Python, project management, communication, etc).

    Return the output as a JSON object with the following structure:
    {{
    "education_level": "<highest level of education>",
    "required_experience_field": "<type of experience>",
    "required_experience_time": "<number of years in field>",
    "skills": ["<skill1>", "<skill2>", ...]
    }}

    Job Description:
    \"\"\"
    {job_posting_text}
    \"\"\"
    """
    response = ollama.generate(
        model="mistral:7b",
        prompt=prompt,
        stream=False
    )
    result = response['response']
    try:
        loaded_data = json.loads(t)
    except:
        match = re.search(r"```json\s*(.*?)\s*```", t, re.DOTALL)
        if not match:
            raise ValueError("No JSON block found in the string.")
        data = match.group(1)
        loaded_data = json.loads(data)
    return loaded_data