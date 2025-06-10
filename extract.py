import fitz    # from pymupdf library
import re
from reportlab.pdfgen import canvas   # canvas from reportlab 
from reportlab.lib.pagesizes import A4
import textwrap
from deep_translator import GoogleTranslator



def is_heading(line):
    line_clean = line.strip()
    return (
        len(line_clean) > 10 and
        line_clean.isupper() and
        not any(char.isdigit() for char in line_clean)
    )


def heading_contains_keywords(heading, keywords):
    return heading.strip().lower() in [kw.lower() for kw in keywords]

def extract_eligibility_criteria(pdf_path):
    start_keywords = ['qualification', 'eligibility', 'mandatory eligibility criteria', 
                      'financial criteria', 'bid capacity criteria', 'participate for bidding']
    stop_keywords = ['bid capacity', 'compensation', 'scope of work', 
                     'clause', 'asphalt plant.']
    irrelevant_phrases = ['financial year', 'compounded', 'multiplying', 'applicable factor' ]
    heading_keywords = ['mandatory eligibility criteria','eligibility criteria']

    doc = fitz.open(pdf_path)
    all_lines = []
    extracted_text = ""

    # First pass: collecting all lines & check for headings
    found_heading = False
    for page in doc:
        page_lines = page.get_text().split('\n')
        all_lines.extend(page_lines)
        for line in page_lines:
            if is_heading(line.strip()) and heading_contains_keywords(line.strip(), heading_keywords):
                found_heading = True

    # Second pass: extract based on heading mode if heading exists
    if found_heading:
        collecting = False
        for line in all_lines:
            stripped = line.strip()
            if is_heading(stripped):
                if heading_contains_keywords(stripped, heading_keywords):
                    collecting = True
                    extracted_text += "\n" + "-"*160 + "\n"
                    extracted_text += f"[HEADING] {stripped}\n"   # [HEADING] 
                else:
                    collecting = False
                continue
            if collecting:
                extracted_text += stripped + "\n"
    else:
        # 3️⃣ Fallback to line-based extraction
        start_flag = False
        for line in all_lines:
            cleaned_line = line.strip()

            if not start_flag:
                if any(kw in cleaned_line.lower() for kw in start_keywords):
                    if any(phrase in cleaned_line.lower() for phrase in irrelevant_phrases):
                        continue
                    start_flag = True
                    extracted_text += "\n" + "-"*160 + "\n"
                    extracted_text += cleaned_line + '\n'
                continue

            if start_flag:
                if any(kw in cleaned_line.lower() for kw in stop_keywords):
                    start_flag = False
                    extracted_text += "\n" + "-"*160 + "\n"
                    continue
                if any(phrase in cleaned_line.lower() for phrase in irrelevant_phrases):
                    continue
                extracted_text += cleaned_line + '\n'

    doc.close()
    return extracted_text.strip()




def save_pdf(text, output_pdf_path):
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 12)
 

    # Starting from the top of the page
    y = height - 50

    # Wrap long lines
    wrapper = textwrap.TextWrapper(width=100)

    for paragraph in text.split('\n'):
        lines = wrapper.wrap(paragraph)

        for line in lines:
            if y < 50:  # New page if out of vertical space
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50

            c.drawString(50, y, line)
            y -= 15

    c.save()


'''
text1 = extract_eligibility_criteria('TenderDocument1.pdf')
output_pdf_path1 = 'outputPDF1.pdf'
'''