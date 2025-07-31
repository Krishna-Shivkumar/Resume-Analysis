import json
import ollama
import re
import os
from google import genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()
api_k = os.getenv("API_KEY")
# try:
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "intern-api-use.json"
# except:
#     print("Key Not Found")
client = genai.Client(
    api_key=api_k
)


def job_info(job_posting_text):
    prompt = f"""
    DO NOT INCLUDE ANY COMMENTS WITHIN THE JSON STRUCTURE
    From the job description below, extract the following:
    1. The highest required level of education (e.g. High School, Bachelor's Degree, Master's Degree, PhD).
    2. The type of experience required (e.g. software engineering, prior experience in customer service, etc).
    3. The amount of time spent in the field
    4. A list of relevant skills (e.g. Python, project management, communication, etc).

    Return the output as a JSON object with the following structure:
    {{
    "education_level": "<highest level of education>",
    "required_experience_field": "<type of experience>",
    "required_experience_time": "<number of years in field>(int)",
    "skills": ["<skill1>", "<skill2>", ...]
    }}
    Job Description:
    \"\"\"
    {job_posting_text}
    \"\"\"
    Please return the structure in a valid JSON format.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= prompt,
    )
    result = response.text
    result = re.sub(r'//.*', '', result)
    # Remove /* */ block comments
    result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
    print(result)
    try:
        loaded_data = json.loads(result)
    except:
        match = re.search(r"```json\s*(.*?)\s*```", result, re.DOTALL)
        if not match:
            raise ValueError("No JSON block found in the string.")
        data = match.group(1)
        loaded_data = json.loads(data)
    return loaded_data