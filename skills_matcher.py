from typing import List, Dict, Tuple
import re
import spacy
from rapidfuzz import fuzz

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Define synonym mappings
SYNONYMS = {
    "nlp": ["natural language processing"],
    "ai": ["artificial intelligence"],
    "ml": ["machine learning"],
    "deep learning": ["neural networks"],
    "data analysis": ["data analytics", "data exploration"],
    "sql": ["structured query language"],
    "excel": ["microsoft excel", "spreadsheet"],
    "python": ["pythonic"],
    "tensorflow": ["tf"],
    "scikit-learn": ["sklearn"],
}

# Normalize text (lowercase, remove special characters)
def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

# Expand skill set with synonyms
def expand_skills(skills: List[str]) -> List[str]:
    expanded = set(skills)
    for skill in skills:
        if skill in SYNONYMS:
            expanded.update(SYNONYMS[skill])
    return list(expanded)

# Lemmatize resume text and return set of lemmas
def get_lemmas(text: str) -> set:
    doc = nlp(text)
    return set([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

# Check if skill is matched in text using word boundaries
def skill_in_text(skill: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(skill)}\b", text) is not None

# Optionally use fuzzy matching
def fuzzy_match(skill: str, text: str, threshold: int = 85) -> bool:
    for word in text.split():
        if fuzz.token_set_ratio(skill, word) >= threshold:
            return True
    return False

# Match skills using exact, synonym, and lemmatized comparison
def match_skills(resume_text: str, required_skills: List[str]) -> Tuple[int, List[str]]:
    text_clean = normalize_text(resume_text)
    lemmas = get_lemmas(text_clean)
    expanded_skills = expand_skills(required_skills)

    matched = []
    for skill in expanded_skills:
        skill_lemma = normalize_text(skill)
        if (
            skill_in_text(skill_lemma, text_clean)
            or skill_lemma in lemmas
            or fuzzy_match(skill_lemma, text_clean)
        ):
            matched.append(skill)
    return len(set(matched)), list(set(matched))

# Process all resumes and categorize them by match quality
def process_resumes(resume_texts: Dict[str, str], required_skills: List[str]):
    results = {}
    matched, missing = {}, {}

    for name, text in resume_texts.items():
        count, matched_skills = match_skills(text, required_skills)
        summary = {
            "score": f"{count}/{len(required_skills)}",
            "matched_skills": matched_skills,
        }
        results[name] = summary
        (matched if count > 0 else missing)[name] = summary

    return {
        "all_results": results,
        "matched_resumes": matched,
        "missing_resumes": missing
    }