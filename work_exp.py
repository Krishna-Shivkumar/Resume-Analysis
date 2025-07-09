import json
import ollama
import re
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

def work_experience(resume_text,topic):
    prompt = f"""
    Extract all work experiences from the resume below relevent to:" {topic}.  Do not include Education experience here.
    Return the output as a JSON array with fields: job_title, company, start_date, end_date.
    Return the output as ONLY a JSON object with the following structure:
    {{
        "job_title": "<title>",
        "company": "<company name>",
        "start_date": "<either month & year or year, never null>",
        "end_date": "<either month & year, only year, or 'present', never null>"
    }}
    DO NOT INCLUDE ANY COMMENTS WITHIN THE JSON STRUCTURE
    Resume:
    \"\"\"
    {resume_text}
    \"\"\"
    """
    # Send the prompt to Ollama (default at localhost:11434)
    response = ollama.generate(
        model= "mistral:7b",
        prompt= prompt,
        stream= False)
    
    
    # Parse and print the model's response
    result = response['response']
    print(result)
    return result

def parse_date(date_str):
    """Convert strings like 'June 2018' or 'Jan 2020' to datetime objects."""
    date_str = date_str.strip()
    if date_str.lower() == "present":
        return datetime.today()
    for fmt in ("%B %Y", "%b %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None  # fallback


def work_time(t):
    t = re.sub(r'//.*', '', t)
    # Remove /* */ block comments
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.DOTALL)
    try:
        loaded_data = json.loads(t)
    except:
        match = re.search(r"```json\s*(.*?)\s*```", t, re.DOTALL)
        if not match:
            raise ValueError("No JSON block found in the string.")
        data = match.group(1)
        loaded_data = json.loads(data)
    # Calculate total experience in months
    total_months = 0
    for job in loaded_data:
        start = parse_date(job["start_date"])
        end = parse_date(job["end_date"])
        print(str(start)+" "+str(end))
        if start and end:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months
    return total_months/12


