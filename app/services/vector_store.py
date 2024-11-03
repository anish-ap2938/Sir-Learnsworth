# app/services/vector_store.py

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from app.config.config import Config
import openai

# Set the OpenAI API key
openai.api_key = Config.OPENAI_API_KEY

def create_vector_store(text_chunks):
    # Initialize the OpenAI Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store
