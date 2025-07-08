import re
from typing import Optional, Tuple

def wordIn(main_string, substring):
        return re.search(r'\b' + re.escape(substring) + r'\b', main_string, re.IGNORECASE) is not None

def resume_skill(skills, resume):
    prop = 0
    not_skills = []
    for skill in skills:
        if (wordIn(resume, skill)):
            prop+=1
        else:
            not_skills.append(skill)
    prop/=len(skills)
    return prop, not_skills

EDUCATION_LEVELS = [
    ("high school", ["high school", "secondary school", "hs diploma", "ged"]),
    ("associate's", ["associate", "a.a.", "a.s."]),
    ("bachelor's", ["bachelor", "b.a.", "b.s.", "undergraduate", "college degree"]),
    ("master's", ["master", "m.a.", "m.s.", "postgraduate"]),
    ("phd", ["ph.d", "phd", "doctorate", "doctoral"]),
]

def extract_highest_education(text: str) -> Optional[str]:
    """Extract the highest education level from text."""
    for level, keywords in reversed(EDUCATION_LEVELS):
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                return level
    return "Education Level Not Found"

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
    return ""