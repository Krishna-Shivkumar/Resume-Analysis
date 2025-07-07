import re
from datetime import datetime
from dateparser import parse as parse_date
from typing import List, Dict, Optional

SKILLS_DB = [
    "python", "sql", "java", "aws", "machine learning", "docker",
    "tableau", "react", "pandas", "excel", "power bi"
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_contacts(text: str) -> Dict[str, Optional[str]]:
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.findall(r"\+?\d[\d\s().-]{7,}\d", text)
    return {
        "email": email[0] if email else None,
        "phone": phone[0] if phone else None
    }


def extract_skills(text: str, skills_db: List[str]) -> List[str]:
    found_skills = [skill for skill in skills_db if skill.lower() in text]
    return list(set(found_skills))


def extract_experience_blocks(text: str) -> str:
    sections = re.split(r"(?i)(experience|work history|employment)", text)
    for i in range(len(sections)):
        if sections[i].lower().strip() in ["experience", "work history", "employment"]:
            return sections[i + 1]
    return ""


def parse_date_range(start_str: str, end_str: Optional[str]) -> Optional[tuple[datetime, datetime]]:
    start = parse_date(start_str)
    end = parse_date(end_str) if end_str and "present" not in end_str.lower() else datetime.today()
    return (start, end) if start and end else None


def extract_job_entries(text: str) -> List[Dict]:
    jobs = []
    pattern = r"(?P<title>.*?)\s*(?:at\s+(?P<company>.*?))?\s*\((?P<start>.*?)(?:\s*[-\u2013]\s*(?P<end>.*?))?\)"
    matches = re.finditer(pattern, text)
    for match in matches:
        data = match.groupdict()
        date_range = parse_date_range(data['start'], data.get('end'))
        if date_range:
            start, end = date_range
            months = (end.year - start.year) * 12 + (end.month - start.month)
            jobs.append({
                "title": data['title'].strip(),
                "company": data['company'].strip() if data['company'] else None,
                "start": start.strftime("%Y-%m"),
                "end": end.strftime("%Y-%m"),
                "months": months
            })
    return jobs


def compute_total_experience(jobs: List[Dict]) -> int:
    return sum(job['months'] for job in jobs)


def extract_entities(text: str) -> Dict:
    text = clean_text(text)
    contact_info = extract_contacts(text)
    skills = extract_skills(text, SKILLS_DB)
    experience_text = extract_experience_blocks(text)
    jobs = extract_job_entries(experience_text)
    total_months = compute_total_experience(jobs)

    return {
        "email": contact_info['email'],
        "phone": contact_info['phone'],
        "skills": skills,
        "experience": jobs,
        "total_experience_months": total_months,
        "text": text  
    }