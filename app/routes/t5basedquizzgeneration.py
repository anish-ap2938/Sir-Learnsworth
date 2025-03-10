import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import PyPDF2

# ----------------------------
# Helper Functions
# ----------------------------
def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF using PyPDF2.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def truncate_text(text, tokenizer, max_tokens=1024):
    """
    Truncate the text to a maximum number of tokens.
    """
    encoded = tokenizer(text, truncation=True, max_length=max_tokens, return_tensors="pt")
    truncated = tokenizer.decode(encoded["input_ids"][0], skip_special_tokens=True)
    return truncated

@st.cache_resource(show_spinner=False)
def load_model():
    """
    Load a small, instruction-tuned model for text generation.
    We use 'google/flan-t5-small' which has about 250M parameters.
    """
    model_name = "google/flan-t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    # Using the text2text-generation pipeline for summarization and quiz generation.
    gen_pipeline = pipeline(
        "text2text-generation", 
        model=model, 
        tokenizer=tokenizer, 
        device=-1  # -1 forces CPU; if you have a GPU, remove or set device=0
    )
    return gen_pipeline, tokenizer

# ----------------------------
# Streamlit App UI
# ----------------------------
st.title("PDF Summary & Quiz Generation")

# PDF File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
    
    if extracted_text:
        st.subheader("Extracted Text (Truncated)")
        gen_pipeline, tokenizer = load_model()
        truncated_text = truncate_text(extracted_text, tokenizer, max_tokens=1024)
        st.text_area("Text (up to 1024 tokens)", truncated_text, height=300)
        
        if st.button("Generate Summary and Quiz"):
            # Generate a concise summary
            summary_prompt = f"Summarize the following text in a concise paragraph:\n\n{truncated_text}"
            with st.spinner("Generating summary..."):
                summary_result = gen_pipeline(
                    summary_prompt, 
                    max_new_tokens=150, 
                    truncation=True
                )
                summary = summary_result[0]['generated_text']
            st.subheader("Summary")
            st.text_area("Summary", summary, height=150)
            
            # Generate a quiz with exactly 5 questions
            quiz_prompt = (
                "Based on the following text, create exactly 5 numbered quiz questions "
                "and provide short answers for each question:\n\n" + truncated_text
            )
            with st.spinner("Generating quiz..."):
                quiz_result = gen_pipeline(
                    quiz_prompt, 
                    max_new_tokens=300, 
                    truncation=True
                )
                quiz = quiz_result[0]['generated_text']
            st.subheader("Quiz (5 Questions)")
            st.write(quiz)
    else:
        st.error("No text could be extracted from the PDF. Please try another file.")
