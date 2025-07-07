import re
from typing import List, Dict, Tuple

def normalize_text(text: str) -> str:
    """Lowercase and remove special characters."""
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

def skill_in_text(skill: str, text: str) -> bool:
    """Use word boundaries to avoid partial matches."""
    return re.search(rf'\b{re.escape(skill)}\b', text) is not None

def match_skills(resume_text: str, required_skills: List[str]) -> Tuple[int, List[str]]:
    """Return number and list of matched skills."""
    text_clean = normalize_text(resume_text)
    matched = [skill for skill in required_skills if skill_in_text(skill, text_clean)]
    return len(matched), matched

def process_resumes(resume_texts: Dict[str, str], required_skills: List[str]):
    """Process each resume and categorize based on skill match count."""
    all_results = {}
    matched_resumes = {}
    missing_resumes = {}

    for name, text in resume_texts.items():
        count, matched = match_skills(text, required_skills)
        result = {
            "score": f"{count}/{len(required_skills)}",
            "matched_skills": matched
        }
        all_results[name] = result
        (matched_resumes if count > 0 else missing_resumes)[name] = result

    return {
        "all_results": all_results,
        "matched_resumes": matched_resumes,
        "missing_resumes": missing_resumes
    }
