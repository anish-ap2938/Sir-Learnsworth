from flask import Blueprint, request, jsonify, render_template, session
from app.services.quiz_service import generate_quiz
from app.services.pdf_service import process_document
from werkzeug.utils import secure_filename
import os

quiz_bp = Blueprint("quiz", __name__)

# Global dictionary to store quizzes per user
user_quizzes = {}

@quiz_bp.route("/quiz_ui", methods=["GET"])
def quiz_ui():
    return render_template("quiz.html")

@quiz_bp.route("/generate_quiz", methods=["POST"])
def generate_quiz_route():
    try:
        data = request.form
        user_id = session.get("user_id", "default_user")
        
        num_questions = int(data.get("num-questions", 5))
        quiz_topic = data.get("quiz-topic")
        difficulty_level = data.get("difficulty-level", "medium")
        
        # Check if a knowledge base has been uploaded
        if "pdf-upload" in request.files:
            pdf_files = request.files.getlist("pdf-upload")
            pdf_texts = []
            for pdf in pdf_files:
                filename = secure_filename(pdf.filename)
                pdf_text = process_document(pdf)
                pdf_texts.append(pdf_text)
            combined_text = " ".join(pdf_texts)
        else:
            combined_text = ""
            if not quiz_topic:
                return jsonify({"error": "Please provide a topic focus if no knowledge base is uploaded."}), 400
        
        # Generate quiz using the service
        quiz = generate_quiz(
            num_questions=num_questions,
            topic=quiz_topic,
            difficulty=difficulty_level,
            knowledge_base=combined_text
        )
        
        # Store the quiz in the global dictionary
        user_quizzes[user_id] = quiz
        
        return jsonify({"message": "Quiz generated successfully.", "quiz": quiz})
    except Exception as e:
        print("Error in /generate_quiz route:", e)
        return jsonify({"error": "An error occurred while generating the quiz."}), 500
