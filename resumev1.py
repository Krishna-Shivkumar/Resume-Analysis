import json
import ollama
from PyPDF2 import PdfReader
 
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)
print('reached1')
resume_text = extract_text_from_pdf('resume.pdf')
print('reached2')
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
print("\n=== Raw LLM Response ===\n")
print(result)
 
# Optionally try parsing it as JSON (if well formatted)
try:
    experience_data = json.loads(result)
    print("\n=== Parsed Experience JSON ===\n")
    print(json.dumps(experience_data, indent=2))
except Exception as e:
    print("\nWarning: Could not parse as JSON.")
    print(e) 