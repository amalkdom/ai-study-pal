@main.route("/dashboard")
@login_required
def dashboard():

    results = QuizResult.query.filter_by(
        user_id=current_user.id
    ).all()

    scores = [r.score for r in results if isinstance(r.score, int)]

    total_quizzes = len(scores)

    if total_quizzes > 0:
        average = round(sum(scores) / total_quizzes, 1)
        highest = max(scores)
        lowest = min(scores)
    else:
        average = 0
        highest = 0
        lowest = 0

    return render_template(
        "dashboard.html",
        scores=scores,
        average=average,
        total_quizzes=total_quizzes,
        highest=highest,
        lowest=lowest
    )
