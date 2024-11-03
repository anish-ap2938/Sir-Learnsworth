from flask import Blueprint, request, jsonify
from app.db import conversations_container
from app.services.ai_service import generate_response

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data["user_id"]
    message = data["message"]

    # Fetch conversation history
    conversation = conversations_container.read_item(user_id, partition_key=user_id) or []
    response = generate_response(message, conversation)

    # Store message and response in conversation history
    conversations_container.upsert_item({
        "id": user_id,
        "history": conversation.get("history", []) + [{"user": message, "bot": response}]
    })

    return jsonify({"response": response})
