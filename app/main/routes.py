from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.ai_quiz import generate_quiz
from app.services.ai_tutor import ask_tutor
from app.models.user import User
from app import db

# Create blueprint
main = Blueprint("main", __name__)


@main.route("/")
def landing():
    return render_template("landing.html")


@main.route("/dashboard")
@login_required
def dashboard():

    scores = [60, 70, 75, 80, 85]

    return render_template(
        "dashboard.html",
        scores=scores,
        total_quizzes=len(scores),
        average_score=sum(scores) // len(scores),
        predicted_score=82,
        streak_days=5
    )


@main.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    questions = None

    if request.method == "POST":
        topic = request.form["topic"]
        questions = generate_quiz(topic)

    return render_template(
        "quiz.html",
        questions=questions
    )


@main.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():

    answer = None

    if request.method == "POST":
        question = request.form["question"]
        answer = ask_tutor(question)

    return render_template(
        "chatbot.html",
        answer=answer
    )


@main.route("/leaderboard")
@login_required
def leaderboard():

    users = User.query.order_by(User.total_score.desc()).limit(10).all()

    return render_template(
        "leaderboard.html",
        users=users
    )


@main.route("/admin")
@login_required
def admin():

    total_users = User.query.count()

    users = User.query.all()

    avg_score = 0
    if len(users) > 0:
        avg_score = sum([u.total_score for u in users]) / len(users)

    return render_template(
        "admin.html",
        total_users=total_users,
        avg_score=avg_score
    )
