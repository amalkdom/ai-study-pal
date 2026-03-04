from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_user
from app.models.user import User
from app import db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for("main.dashboard"))

    return render_template("register.html")register.html")
