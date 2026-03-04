from flask import Blueprint, render_template, request
from flask_login import login_required

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("landing.html")


@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    if request.method == "POST":
        topic = request.form.get("topic")

    return render_template("quiz.html")
