from flask import Blueprint, request, jsonify, redirect, url_for, session
from app.db import users_container
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")

    # Check if user already exists
    existing_user = list(users_container.query_items(
        query="SELECT * FROM users u WHERE u.username=@username",
        parameters=[{"name": "@username", "value": username}],
        enable_cross_partition_query=True
    ))
    
    if existing_user:
        return jsonify({"message": "Username already exists"}), 409
    
    # Hash the password and store user details
    hashed_password = generate_password_hash(password)
    user_data = {
        "id": username,
        "username": username,
        "password": hashed_password
    }
    users_container.create_item(user_data)
    return redirect(url_for("login_page"))

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Retrieve user from the database
    user = list(users_container.query_items(
        query="SELECT * FROM users u WHERE u.username=@username",
        parameters=[{"name": "@username", "value": username}],
        enable_cross_partition_query=True
    ))
    
    if user and check_password_hash(user[0]["password"], password):
        session["logged_in"] = True
        return redirect(url_for("index"))
    
    return jsonify({"message": "Invalid credentials"}), 401

# Define the logout route
@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Clear session to log the user out
    return redirect(url_for("login_page"))
