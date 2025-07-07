import string
import pdfplumber
import docx
from io import BytesIO
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Extract and clean keywords from raw text
def extract_keywords(text):
    ps = PorterStemmer()
    stop_words = set(stopwords.words('english'))

    tokens = word_tokenize(text.lower())
    keywords = []

    for token in tokens:
        token = token.translate(str.maketrans('', '', string.punctuation))
        if token.isalpha() and token not in stop_words and len(token) > 2:
            keywords.append(ps.stem(token))

    return list(set(keywords))  # unique

# Load and clean text from job description file (TextIO or BytesIO)
def load_job_description(file_obj):
    ext = file_obj.lower().split('.')[-1]
    if ext == 'pdf':
        text = extract_pdf_keywords(file_obj)
    elif ext == 'docx':
        text = extract_docx_keywords(file_obj)
    else:
        text = file_obj.read()
        if isinstance(text, bytes):
            text = text.decode('utf-8')
    return extract_keywords(text)

# Extract keywords from PDF (BytesIO or open file)
def extract_pdf_keywords(file_obj):
    with pdfplumber.open(file_obj) as pdf:
        text = ''.join(page.extract_text() or '' for page in pdf.pages)
    return extract_keywords(text)

# Extract keywords from DOCX (BytesIO or open file)
def extract_docx_keywords(file_obj):
    doc = docx.Document(file_obj)
    text = '\n'.join(p.text for p in doc.paragraphs)
    return extract_keywords(text)

# Keyword comparison
def compare_keywords(resume_keywords, job_keywords):
    matched = [k for k in resume_keywords if k in job_keywords]
    missing = [k for k in job_keywords if k not in resume_keywords]
    match_percent = round(len(matched) / len(job_keywords) * 100, 2) if job_keywords else 0.0

    return {
        "matched": matched,
        "missing": missing,
        "match_percent": match_percent
    }

# Example function usage (for testing or integration)
def analyze_resume(resume_file, job_file, resume_type='pdf'):
    job_keywords = load_job_description(job_file)

    if resume_type == 'pdf':
        resume_keywords = extract_pdf_keywords(resume_file)
    elif resume_type == 'docx':
        resume_keywords = extract_docx_keywords(resume_file)
    elif resume_type =='txt':
        text = resume_file.read()
        if isinstance(text, bytes):
            text = text.decode('utf-8')
    else:
        raise ValueError("Unsupported resume type: must be 'pdf', 'docx', or 'txt'")

    return compare_keywords(resume_keywords, job_keywords)