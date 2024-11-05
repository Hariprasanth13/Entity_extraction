import pdfplumber
import json

def extract_text_from_pdf(pdf_path):
    extracted_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            extracted_text.append(page_text)
    return extracted_text

def convert_to_json(text):
    # Convert the list of text from each page to JSON format
    json_data = json.dumps(text)
    return json_data

pdf_path = "C:\\Projects\\GBS_project\\GBS_EE\\FRANCE_FGXPO\\20624606.pdf"
extracted_text = extract_text_from_pdf(pdf_path)
json_data = convert_to_json(extracted_text)
print(json_data)