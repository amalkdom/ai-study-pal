@main.route("/admin")
@login_required
def admin_dashboard():

    from app.models.user import User

    total_users = User.query.count()

    users = User.query.all()

    avg_score = sum([u.total_score for u in users]) / max(len(users),1)

    return render_template(
        "admin.html",
        total_users=total_users,
        avg_score=avg_score
    )
