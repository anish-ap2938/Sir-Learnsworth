from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from app.services.vector_store import get_vector_store

def generate_response(user_message, conversation_history):
    vector_store = get_vector_store(conversation_history)
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key="OPENAI_API_KEY")
    memory = ConversationBufferMemory.from_messages(conversation_history)
    conversation_chain = ConversationalRetrievalChain(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
    )
    return conversation_chain({"input": user_message})
