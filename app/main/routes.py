from flask import Blueprint, render_template, request
from flask_login import login_required
from app.services.ai_quiz import generate_quiz

main = Blueprint("main", __name__)

@main.route("/")
def landing():
    return render_template("landing.html")


@main.route("/dashboard")
@login_required
def dashboard():

    scores=[65,70,75,80,85]

    return render_template(
        "dashboard.html",
        scores=scores,
        total_quizzes=len(scores),
        average_score=sum(scores)//len(scores)
    )


@main.route("/quiz",methods=["GET","POST"])
@login_required
def quiz():

    questions=None

    if request.method=="POST":

        topic=request.form["topic"]

        questions=generate_quiz(topic)

    return render_template(
        "quiz.html",
        questions=questions
    )
