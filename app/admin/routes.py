from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import User
from app.models.quiz import Quiz
from app.models.ai_usage import AIUsage
from app import db
from sqlalchemy import func

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return "Unauthorized", 403

    total_users = User.query.count()
    total_quizzes = Quiz.query.count()

    avg_score = db.session.query(func.avg(Quiz.score)).scalar() or 0

    total_ai_calls = AIUsage.query.count()

    weakest_topic = db.session.query(
        Quiz.topic,
        func.avg(Quiz.score).label("avg_score")
    ).group_by(Quiz.topic).order_by("avg_score").first()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_quizzes=total_quizzes,
        avg_score=round(avg_score, 2),
        total_ai_calls=total_ai_calls,
        weakest_topic=weakest_topic
    )
