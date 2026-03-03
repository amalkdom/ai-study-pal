from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import User
from app.models.quiz import Quiz
from app.models.performance import Performance

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403

    total_users = User.query.count()
    total_quizzes = Quiz.query.count()
    performances = Performance.query.all()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_quizzes=total_quizzes,
        performances=performances
    )
