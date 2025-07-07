import re
from typing import Optional, Tuple

# Ordered education levels from lowest to highest
EDUCATION_LEVELS = [
    ("high school", ["high school", "secondary school", "hs diploma", "ged"]),
    ("associate's", ["associate", "a.a.", "a.s."]),
    ("bachelor's", ["bachelor", "b.a.", "b.s.", "undergraduate", "college degree"]),
    ("master's", ["master", "m.a.", "m.s.", "postgraduate"]),
    ("phd", ["ph.d", "phd", "doctorate", "doctoral"]),
]

def normalize_text(text: str) -> str:
    """Lowercase and remove special characters."""
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

def extract_highest_education(text: str) -> Optional[str]:
    """Extract the highest education level from text."""
    for level, keywords in reversed(EDUCATION_LEVELS):
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                return level
    return None

def extract_major(text: str) -> Optional[str]:
    """
    Extract major or field of study.
    Looks for patterns like 'bachelor of science in ___' or 'major in ___'.
    """
    patterns = [
        r"bachelor(?:'s)? of (?:arts|science) in ([a-z\s]+)",
        r"master(?:'s)? of (?:arts|science) in ([a-z\s]+)",
        r"ph\.?d\.? in ([a-z\s]+)",
        r"major in ([a-z\s]+)",
        r"degree in ([a-z\s]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None

def is_major_relevant(major: str, job_description: str) -> bool:
    """
    Check if the major has overlap with job description keywords.
    This is a basic keyword match. You can improve it with embeddings or TF-IDF.
    """
    job_keywords = set(normalize_text(job_description).split())
    major_keywords = set(normalize_text(major).split())
    return len(major_keywords & job_keywords) > 0

def evaluate_education_relevance(resume_text: str, job_description: str) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Returns (highest_education_level, major, is_major_relevant).
    """
    clean_resume = normalize_text(resume_text)
    level = extract_highest_education(clean_resume)
    major = extract_major(clean_resume)
    relevance = is_major_relevant(major, job_description) if major else False
    return level, major, relevance
