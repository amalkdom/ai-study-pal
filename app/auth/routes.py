from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app import db

auth = Blueprint("auth", __name__)

# ---------------- LOGIN PAGE ----------------
@auth.route("/")
def login():
    return render_template("login.html")


# ---------------- REGISTER ----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        age = request.form.get("age")
        student_class = request.form.get("class")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.")
            return redirect(url_for("auth.login"))

        # Create new user
        user = User(
            name=name,
            age=age,
            student_class=student_class,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------- LOGIN POST ----------------
@auth.route("/login", methods=["POST"])
def login_post():

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found.")
        return redirect(url_for("auth.login"))

    if not user.check_password(password):
        flash("Incorrect password.")
        return redirect(url_for("auth.login"))

    login_user(user)
    return redirect(url_for("main.dashboard"))


# ---------------- LOGOUT ----------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
