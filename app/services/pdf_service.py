from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from langchain.text_splitter import CharacterTextSplitter

def process_document(file):
    text = ""
    if file.content_type == "application/pdf":
        text = get_pdf_text(file)
    # Add support for DOC, images, etc.
    return text

def get_pdf_text(file):
    pdf_reader = PdfReader(file)
    text = "".join(page.extract_text() for page in pdf_reader.pages)
    return text
