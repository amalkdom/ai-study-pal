@main.route("/dashboard")
@login_required
def dashboard():

    results = QuizResult.query.filter_by(
        user_id=current_user.id
    ).all()

    scores = []
    for r in results:
        try:
            scores.append(int(r.score))
        except:
            scores.append(0)

    average = 0
    if len(scores) > 0:
        average = round(sum(scores) / len(scores), 1)

    return render_template(
        "dashboard.html",
        scores=scores,
        average=average
    )
