from flask import Blueprint, render_template
from flask_login import login_required
from app.models.user import User

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("login.html")


@main.route("/dashboard")
@login_required
def dashboard():

    # Example analytics data
    total_quizzes = 8
    average_score = 76
    predicted_score = 82
    streak_days = 5

    scores = [60, 70, 75, 80, 65, 85, 78, 90]

    return render_template(
        "dashboard.html",
        total_quizzes=total_quizzes,
        average_score=average_score,
        predicted_score=predicted_score,
        streak_days=streak_days,
        scores=scores
    )


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


@main.route("/leaderboard")
@login_required
def leaderboard():

    users = User.query.order_by(User.total_score.desc()).limit(10).all()

    return render_template(
        "leaderboard.html",
        users=users
    )
