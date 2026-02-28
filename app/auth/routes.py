from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app import db

auth = Blueprint(
    "auth",
    __name__,
    template_folder="../templates"
)

# ---------------- LOGIN PAGE ----------------

@auth.route("/")
def login():
    return render_template("login.html")


# ---------------- REGISTER ----------------

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        existing_user = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("auth.register"))

        user = User(
            name=request.form["name"],
            age=request.form["age"],
            student_class=request.form["class"],
            email=request.form["email"]
        )

        user.set_password(request.form["password"])

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------- LOGIN POST ----------------

@auth.route("/login", methods=["POST"])
def login_post():

    user = User.query.filter_by(
        email=request.form["email"]
    ).first()

    if not user or not user.check_password(request.form["password"]):
        flash("Invalid email or password.")
        return redirect(url_for("auth.login"))

    login_user(user)
    return redirect(url_for("main.dashboard"))


# ---------------- LOGOUT ----------------

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
