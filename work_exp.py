import json
import ollama
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

def work_experience(resume_text):
    prompt = f"""
    Analyze the resume below and extract structured information relevant to employment qualifications.
    
    Return the output as a single JSON object with the following fields:
    
    {{
        "education_level": "<highest education level mentioned in the resume, e.g., high school, bachelor, master, PhD>",
        "required_experience_field": "<primary area or field of work experience, e.g., clinical psychology, behavioral health>",
        "required_experience_time": "<total years of experience in that field, use decimal years if needed (e.g., 2.5)>",
        "skills": ["<skill1>", "<skill2>", ...],
        "work_experience": [
            {{
                "job_title": "<title>",
                "company": "<company name>",
                "start_date": "<month/year or year>",
                "end_date": "<month/year or 'present'>"
            }}
        ]
    }}
    
    Resume:
    \"\"\"
    {resume_text}
    \"\"\"
    """
    
    print('reached3')

    response = ollama.generate(
        model="mistral:7b",
        prompt=prompt,
        stream=False
    )

    result = response['response']
    print(result)
    return result


def parse_date(date_str):
    """Convert strings like 'June 2018' or 'Jan 2020' to datetime objects."""
    date_str = date_str.strip()
    if date_str.lower() == "present":
        return datetime.today()
    for fmt in ("%B %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def work_time(t):
    """
    Parse work experience duration from input string `t`.
    First tries to extract JSON block and calculate from structured data.
    If no JSON found, fallback to regex extraction of years of experience from plain text.
    """
    try:
        loaded_data = json.loads(t)
        # If loaded_data is string (raw AI text), it might fail below
        if isinstance(loaded_data, str):
            raise ValueError("Loaded JSON is a string, retry with regex.")
    except Exception:
        # Try to find JSON block inside string with ```json ... ```
        match = re.search(r"```json\s*(.*?)\s*```", t, re.DOTALL)
        if not match:
            # fallback: try to find any JSON object {...}
            match = re.search(r"\{.*?\}", t, re.DOTALL)
        if match:
            data = match.group(1)
            loaded_data = json.loads(data)
        else:
            # No JSON found — fallback: extract years of experience from plain text via regex
            match_exp = re.search(
                r"(\d+(\.\d+)?)\s*(?:years|yrs)\s*(?:of)?\s*(experience|work)", t, re.IGNORECASE
            )
            if match_exp:
                return float(match_exp.group(1))
            # If nothing found, assume 0 experience (or -1 if you prefer)
            return 0

    # If we have JSON structured data, calculate total months from work_experience list
    work_entries = loaded_data.get("work_experience", [])
    total_months = 0

    for job in work_entries:
        start = parse_date(job.get("start_date", ""))
        end = parse_date(job.get("end_date", ""))
        if start and end:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months

    return total_months / 12
