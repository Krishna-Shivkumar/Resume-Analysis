from fpdf import FPDF
from pyresparser import ResumeParser
import nltk

# Ensure stopwords are available
try:
    from nltk.corpus import stopwords
    _ = stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

# # Convert TXT to PDF
# class PDF(FPDF):
#     def header(self):
#         self.set_font("Helvetica", size=12)

# pdf = PDF()
# pdf.add_page()
# pdf.set_font("Helvetica", size=12)

# with open("resume.txt", "r", encoding="utf-8") as f:
#     for line in f:
#         # Handle Unicode that FPDF may not like
#         safe_line = line.replace("–", "-").replace("•", "*").encode('latin-1', 'ignore').decode('latin-1')
#         pdf.multi_cell(0, 10, safe_line.strip())

# pdf.output("your_resume.pdf")

# Parse the resume using pyresparser
data = ResumeParser("resume.pdf").get_extracted_data()
print(data)
