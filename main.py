from flask import Flask, render_template
from flask_cors import CORS
from app.routes.auth import auth_bp
from app.routes.chatbot import chatbot_bp
from app.routes.quiz import quiz_bp
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app with correct template and static folder paths
# app = Flask(__name__, template_folder="app/templates", static_folder="/app/static")
app = Flask(__name__, template_folder="app/templates", static_folder="app/static", static_url_path="/static")

CORS(app)  # Enable CORS for all routes

# Register Blueprints for different routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
app.register_blueprint(quiz_bp, url_prefix="/quiz")

# Define a route for the index page
@app.route("/")
def index():
    return render_template("index.html")

# Main entry point
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)