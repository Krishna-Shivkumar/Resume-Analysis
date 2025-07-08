import json
import ollama
import re
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

def work_experience(resume_text):
    prompt = f"""
    Extract all work experiences from the resume below.
    Return the output as a JSON array with fields: job_title, company, start_date, end_date.
    
    Resume:
    \"\"\"
    {resume_text}
    \"\"\"
    """
    print('reached3')
    # Send the prompt to Ollama (default at localhost:11434)
    response = ollama.generate(
        model= "mistral:7b",
        prompt= prompt,
        stream= False)
    
    
    # Parse and print the model's response
    result = response['response']
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
        if start and end:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months
    return total_months/12


