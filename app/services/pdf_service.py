from docx import Document
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from pdf2image import convert_from_path
import pytesseract
from io import BytesIO

def process_document(file):
    text = ""
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file)
    elif file.content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        text = extract_text_from_doc(file)
    elif file.content_type.startswith("image/"):
        text = extract_text_from_image(file)
    return text

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text() is not None)
    return text

def extract_text_from_doc(file):
    doc = Document(file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extract_text_from_image(file):
    image = convert_from_path(BytesIO(file.read()))
    text = ""
    for img in image:
        text += pytesseract.image_to_string(img)
    return text

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)
