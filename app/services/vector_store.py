from langchain_openai import OpenAIEmbeddings  # Updated import from the new package
from langchain.vectorstores import FAISS

def create_vector_store(text_chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vector_store
