# app/routes/chatbot.py

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from app.services.ai_service import generate_response, generate_quiz_from_conversation
from app.services.pdf_service import process_document, split_text_into_chunks
from app.services.vector_store import create_vector_store

chatbot_bp = Blueprint("chatbot", __name__)

# Global dictionaries to hold vector stores and conversation chains for each user
vector_stores = {}
conversation_chains = {}
conversation_histories = {}

# Route to render the chatbot HTML page
@chatbot_bp.route("/chat_ui_page", methods=["GET"])
def chat_ui_page():
    if "logged_in" not in session or not session["logged_in"]:
        return redirect(url_for("auth.login"))
    return render_template("chatbot.html")

# Route to handle POST requests for chat messages
@chatbot_bp.route("/chat_ui", methods=["POST"])
def chat_ui():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request data"}), 400

        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))
        message = data.get("message")

        language = session.get("language", "English")
        word_limit = int(session.get("word_limit", 1000))
        focus_areas = session.get("focus_areas", "General understanding")

        # Retrieve vector store and conversation chain for the user from global dictionaries
        vector_store = vector_stores.get(user_id, None)
        conversation_chain = conversation_chains.get(user_id, None)

        response_text, conversation_chain = generate_response(
            user_id,
            message,
            language,
            word_limit,
            focus_areas,
            vector_store,
            conversation_chain
        )

        # Update the conversation chain and history in the global dictionaries
        conversation_chains[user_id] = conversation_chain

        # Maintain conversation history for quiz generation
        conversation_history = conversation_histories.get(user_id, [])
        conversation_history.append({
            "user_message": message,
            "bot_response": response_text
        })
        conversation_histories[user_id] = conversation_history

        return jsonify({"response_text": response_text})
    except Exception as e:
        print("Error in /chat_ui route:", e)
        return jsonify({"error": "An error occurred on the server"}), 500

# Route to handle knowledge base upload
@chatbot_bp.route("/upload_knowledge", methods=["POST"])
def upload_knowledge():
    try:
        language = request.form.get("language-selection")
        word_limit = request.form.get("word-limit")
        focus_areas = request.form.get("focus-areas")
        session["language"] = language
        session["word_limit"] = word_limit
        session["focus_areas"] = focus_areas

        pdf_texts = []
        if "pdf-upload" in request.files:
            pdf_files = request.files.getlist("pdf-upload")
            for pdf in pdf_files:
                if pdf.filename == '':
                    continue
                filename = secure_filename(pdf.filename)
                pdf_text = process_document(pdf)
                pdf_texts.append(pdf_text)

        # Combine text and create vector store for retrieval
        combined_text = " ".join(pdf_texts)
        if not combined_text.strip():
            return jsonify({"error": "Uploaded documents are empty."}), 400

        text_chunks = split_text_into_chunks(combined_text)

        # Create and store the vector store in the global dictionary
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))
        vector_store = create_vector_store(text_chunks)
        vector_stores[user_id] = vector_store  # Store vector store in global dictionary

        # Clear any existing conversation chain and history since knowledge base has been updated
        if user_id in conversation_chains:
            del conversation_chains[user_id]
        if user_id in conversation_histories:
            del conversation_histories[user_id]

        return jsonify({"message": "Knowledge base uploaded and processed successfully"})
    except Exception as e:
        print("Error in /upload_knowledge route:", e)
        return jsonify({"error": "An error occurred during upload"}), 500

# Route to generate quiz from conversation
@chatbot_bp.route("/generate_quiz_from_conversation", methods=["POST"])
def generate_quiz_from_conversation_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400

        num_questions = int(data.get("num_questions", 5))
        difficulty_level = data.get("difficulty_level", "medium")

        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))
        conversation_history = conversation_histories.get(user_id, [])
        if not conversation_history:
            return jsonify({"error": "No conversation history available to generate quiz."}), 400

        # Generate quiz using the service
        quiz = generate_quiz_from_conversation(
            num_questions=num_questions,
            difficulty_level=difficulty_level,
            conversation_history=conversation_history
        )

        return jsonify({"quiz": quiz})
    except Exception as e:
        print("Error in /generate_quiz_from_conversation route:", e)
        return jsonify({"error": "An error occurred while generating the quiz."}), 500
