# app/services/ai_service.py

from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from datetime import datetime
from app.db import conversations_container
from app.config.config import Config
import openai
import json

# Set the OpenAI API key
openai.api_key = Config.OPENAI_API_KEY

def generate_response(user_id, user_message, language, word_limit, focus_areas, vector_store, conversation_chain=None):
    # Define the QA prompt template
    QA_PROMPT_TEMPLATE = f"""
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

                # Create the QA prompt
                qa_prompt = PromptTemplate(
                    template=QA_PROMPT_TEMPLATE,
                    input_variables=["context", "question"]
                )

                # Create the QA chain
                qa_chain = load_qa_chain(llm, chain_type='stuff', prompt=qa_prompt)

                # Create the question condensing prompt
                condense_prompt = PromptTemplate(
                    template="""
Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:""",
                    input_variables=["chat_history", "question"]
                )

                # Create the question generator chain
                question_generator = LLMChain(llm=llm, prompt=condense_prompt)

                # Create the conversational retrieval chain
                conversation_chain = ConversationalRetrievalChain(
                    retriever=retriever,
                    question_generator=question_generator,
                    combine_docs_chain=qa_chain,
                    memory=memory,
                    verbose=False
                )
            else:
                # If no vector store, create a simple conversational chain
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
            # Use existing conversation chain
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


def generate_quiz_from_conversation(num_questions, difficulty_level, conversation_history):
    """
    Generate a quiz based on the conversation history.
    """
    # Combine the conversation history into a single string
    conversation_text = "\n".join([
        f"User: {entry['user_message']}\nBot: {entry['bot_response']}"
        for entry in conversation_history
    ])

    # Create a prompt for the AI model
    prompt = f"""
You are an AI that generates quizzes based on conversation history.

Conversation History:
{conversation_text}

Please create a quiz with {num_questions} questions at a {difficulty_level} difficulty level. Provide the quiz in the following JSON format:

[
    {{
        "question": "Question 1",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A"
    }},
    ...
]
"""

    # Initialize the OpenAI language model
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    try:
        response = llm.predict(prompt)
        quiz_content = response.strip()
        # Parse the generated content into a Python list
        quiz = json.loads(quiz_content)
        return quiz
    except Exception as e:
        print("Error generating quiz from conversation:", e)
        raise e
