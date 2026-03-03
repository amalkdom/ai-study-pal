from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.quiz import Quiz
from app.models.performance import Performance
from app.services.recommendation_engine import generate_recommendation
from app import db
import json

main = Blueprint("main", __name__)

@main.route("/dashboard")
@login_required
def dashboard():

    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    scores = [q.score for q in quizzes if q.score is not None]

    total_quizzes = len(scores)
    average_score = round(sum(scores)/len(scores),1) if scores else 0

    predicted_score = min(100, average_score + 7)

    recommendation = generate_recommendation(current_user.id)

    return render_template(
        "dashboard.html",
        total_quizzes=total_quizzes,
        average_score=average_score,
        predicted_score=predicted_score,
        recommendation=recommendation,
        scores=json.dumps(scores)
    )
