# main.py

from flask import Flask, render_template, redirect, url_for, session
from flask_cors import CORS
from app.routes.auth import auth_bp
from app.routes.chatbot import chatbot_bp
from app.routes.quiz import quiz_bp
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="app/templates", static_folder="app/static", static_url_path="/static")
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Use environment variable for secret key

CORS(app)  # Enable CORS for all routes

# Register Blueprints for different routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
app.register_blueprint(quiz_bp, url_prefix="/quiz")

# Route for index (redirects to login if not authenticated)
@app.route("/")
def index():
    if "logged_in" in session and session["logged_in"]:
        return render_template("homepage.html")
    return redirect(url_for("login_page"))

# Route for login/signup page
@app.route("/login")
def login_page():
    if "logged_in" in session and session["logged_in"]:
        return redirect(url_for("index"))
    return render_template("index.html")

# Main entry point
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
