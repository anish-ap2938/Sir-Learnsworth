import streamlit as st
from huggingface_hub import login
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import PyPDF2
import os

# If running on macOS and you want to disable MPS memory limit:
# os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"

# ----------------------------
# Hugging Face Authentication
# ----------------------------
st.sidebar.header("Hugging Face Authentication")
hf_token = st.sidebar.text_input("Enter your Hugging Face Token:", type="password")

if not hf_token:
    st.sidebar.error("Please enter your Hugging Face token to continue.")
    st.stop()
else:
    login(hf_token)
    st.sidebar.success("Logged in successfully!")

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

def truncate_text(text, gen_pipeline, max_tokens=1024):
    """
    Truncate the text to 'max_tokens' tokens according to the model's tokenizer.
    This prevents excessively large inputs that can exceed the model's context window.
    """
    encoded = gen_pipeline.tokenizer(
        text,
        truncation=True,
        max_length=max_tokens,
        return_tensors="pt"
    )
    truncated = gen_pipeline.tokenizer.decode(encoded["input_ids"][0], skip_special_tokens=True)
    return truncated

@st.cache_resource(show_spinner=False)
def load_3b_llama_model(token):
    """
    Load a 3B-parameter Llama-based model (Open LLaMA 3B) and tokenizer.
    This is smaller than 7B/8B variants, so it should be faster & use less memory.
    """
    model_name = "openlm-research/open_llama_3b"  # 3B model
    st.info("Loading Open LLaMA 3B model. This may take some time...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False, token=token)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cpu",  # Using CPU to avoid GPU memory issues
        trust_remote_code=True,
        token=token
    )
    if model.config.pad_token_id is None:
        model.config.pad_token_id = tokenizer.eos_token_id

    # Create the text-generation pipeline
    gen_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return gen_pipeline

# ----------------------------
# Streamlit App UI
# ----------------------------
st.title("AI Tutor: PDF Summary & 5-Question Quiz (Truncated Input)")

# Load the 3B model pipeline
llama_pipeline = load_3b_llama_model(hf_token)

# PDF File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        
    if extracted_text:
        st.subheader("Extracted Text (Truncated)")
        
        # Truncate the text to avoid going beyond the model's context window
        truncated_text = truncate_text(extracted_text, llama_pipeline, max_tokens=1024)
        
        # Show the truncated text in the UI
        st.text_area("PDF Text (Truncated to 1024 tokens)", truncated_text, height=300)
        
        # Generate both summary and quiz when button is pressed
        if st.button("Generate Summary and Quiz"):
            # Generate Summary
            with st.spinner("Generating summary..."):
                summary_prompt = (
                    "Summarize the following text in a concise paragraph:\n\n"
                    + truncated_text
                )
                summary_result = llama_pipeline(
                    summary_prompt,
                    truncation=True,
                    pad_token_id=llama_pipeline.tokenizer.eos_token_id,
                    max_new_tokens=150
                )
                summary = summary_result[0]['generated_text']
            
            st.subheader("Summary")
            st.text_area("Summary", summary, height=150)
            
            # Generate Quiz
            with st.spinner("Generating quiz..."):
                quiz_prompt = (
                    "Based on the following text, create exactly 5 numbered quiz questions "
                    "and provide short answers for each question.\n\n"
                    + truncated_text
                )
                quiz_result = llama_pipeline(
                    quiz_prompt,
                    truncation=True,
                    pad_token_id=llama_pipeline.tokenizer.eos_token_id,
                    max_new_tokens=300
                )
                quiz = quiz_result[0]['generated_text']
            
            st.subheader("Generated Quiz (5 Questions)")
            st.write(quiz)
    else:
        st.error("No text could be extracted from the PDF. Please try another file.")
