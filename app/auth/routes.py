from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models.user import User
from app import db

auth = Blueprint("auth", __name__)

@auth.route("/")
def login():
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email already exists")
            return redirect(url_for("auth.register"))

        user = User(
            name=request.form["name"],
            email=request.form["email"]
        )
        user.set_password(request.form["password"])

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth.route("/login", methods=["POST"])
def login_post():
    user = User.query.filter_by(email=request.form["email"]).first()

    if user and user.check_password(request.form["password"]):
        login_user(user)
        return redirect(url_for("main.dashboard"))

    flash("Invalid credentials")
    return redirect(url_for("auth.login"))

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
