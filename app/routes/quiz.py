from flask import Blueprint, request, jsonify
from app.services.pdf_service import process_document

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/quiz", methods=["POST"])
def create_quiz():
    data = request.files["document"]
    text = process_document(data)
    questions = [{"question": f"Quiz question on {text[:50]}"}]  # Placeholder for quiz questions
    return jsonify({"questions": questions})
