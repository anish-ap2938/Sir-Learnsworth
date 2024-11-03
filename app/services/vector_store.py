from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def get_vector_store(text_chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vector_store
