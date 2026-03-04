from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint("main", __name__)

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@main.route("/planner")
@login_required
def planner():
    return render_template("planner.html")


@main.route("/performance")
@login_required
def performance():
    return render_template("performance.html")


@main.route("/chatbot")
@login_required
def chatbot():
    return render_template("chatbot.html")


@main.route("/timeline")
@login_required
def timeline():
    return render_template("summary.html")
