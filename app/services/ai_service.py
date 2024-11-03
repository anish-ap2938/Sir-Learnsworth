from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from datetime import datetime
from app.db import conversations_container

def generate_response(user_id, user_message, language, word_limit, focus_areas, vector_store, conversation_chain=None):
    # Adjusted SYSTEM_PROMPT to include placeholders for 'context' and 'question'
    SYSTEM_PROMPT = f"""
You are Sir Learnsworth, an AI Tutor. Answer the following question based on the context provided.
Language: {language}. Word limit: {word_limit}. Focus areas: {focus_areas}.
If no relevant information is found, respond based on your general knowledge.

Context:
{{context}}

Question:
{{question}}

Answer:
"""
    # Initialize the OpenAI language model
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

    try:
        if conversation_chain is None:
            # Initialize conversation chain
            if vector_store:
                retriever = vector_store.as_retriever()
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                # Create PromptTemplate with 'context' and 'question' as input variables
                prompt = PromptTemplate(
                    template=SYSTEM_PROMPT,
                    input_variables=["context", "question"]
                )
                conversation_chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=retriever,
                    memory=memory,
                    combine_docs_chain_kwargs={'prompt': prompt}
                )
            else:
                prompt = PromptTemplate(
                    input_variables=["history", "input"],
                    template="""
{history}
Human: {input}
AI:
"""
                )
                memory = ConversationBufferMemory(memory_key="history", return_messages=True)
                conversation_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
        else:
            # No need to manually update memory; it's handled by the chain
            pass

        # Generate response
        if isinstance(conversation_chain, ConversationalRetrievalChain):
            response = conversation_chain({"question": user_message})
            response_text = response.get("answer", "I'm here to help!")
        else:
            response = conversation_chain({"input": user_message})
            response_text = response.get("text", "I'm here to help!")

    except Exception as e:
        print("Error invoking conversation chain:", e)
        return "Sorry, I'm unable to process your request at the moment.", conversation_chain

    # Save conversation history in Cosmos DB for persistent storage
    try:
        conversation_entry = {
            "id": f"{user_id}_{datetime.utcnow().isoformat()}",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "bot_response": response_text,
            "language": language,
            "word_limit": word_limit,
            "focus_areas": focus_areas
        }
        conversations_container.upsert_item(conversation_entry)
    except Exception as e:
        print("Error saving conversation to database:", e)

    return response_text, conversation_chain
