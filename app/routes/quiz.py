from flask import Blueprint, request, jsonify, render_template
from app.services.pdf_service import process_document

quiz_bp = Blueprint("quiz", __name__)

# Route to render the quiz configuration page
@quiz_bp.route("/quiz", methods=["GET"])
def quiz_ui():
    return render_template("quiz.html")

# POST route to handle quiz creation
@quiz_bp.route("/quiz", methods=["POST"])
def create_quiz():
    data = request.files["document"]
    text = process_document(data)
    questions = [{"question": f"Quiz question on {text[:50]}"}]  # Placeholder for quiz questions
    return jsonify({"questions": questions})
