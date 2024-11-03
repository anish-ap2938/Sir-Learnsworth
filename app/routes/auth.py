from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    return render_template("index.html")

@auth_bp.route("/logout")
def logout():
    # Implement logout logic if needed
    return redirect(url_for("index"))
