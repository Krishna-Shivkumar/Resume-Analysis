import re
from google.cloud import documentai_v1 as documentai

PROJECT_ID = "resume-465414"
LOCATION = "us"
PROCESSOR_ID = "4da0edcaa19b9f53"
FILE_PATH = "resume.pdf"

def extract_resume_fields(text: str) -> dict:
    # Basic regex patterns
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    name = text.strip().split("\n")[0]  # Assume name is first line

    # Extract sections
    def extract_section(start_keywords, text_block):
        pattern = '|'.join(start_keywords)
        split = re.split(pattern, text_block, flags=re.IGNORECASE)
        return split[1].strip() if len(split) > 1 else ""

    education = extract_section(["Education"], text)
    skills = extract_section(["Skills"], text)
    certifications = extract_section(["Certifications", "Licenses"], text)
    experience = extract_section(["Work Experience", "Experience", "Employment"], text)

    return {
        "Name": name,
        "Email": email.group(0) if email else None,
        "Phone": phone.group(0) if phone else None,
        "Education": education,
        "Skills": skills,
        "Certifications": certifications,
        "Experience": experience
    }

def process_document(file_path: str) -> None:
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"

    with open(file_path, "rb") as file:
        file_content = file.read()

    raw_document = documentai.RawDocument(
        content=file_content, mime_type="application/pdf"
    )

    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    document = result.document

    print("✅ Document processed successfully.\n")

    # Extract fields from the full text
    resume_data = extract_resume_fields(document.text)

    print("🔎 Parsed Resume Fields:\n")
    for key, value in resume_data.items():
        print(f"{key}: {value[:300] if isinstance(value, str) else value}\n")  # Truncate long text

if __name__ == "__main__":
    process_document(FILE_PATH)
