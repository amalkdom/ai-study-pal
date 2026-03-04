@main.route("/quiz", methods=["GET","POST"])
@login_required
def quiz():

    from app.services.ai_quiz import generate_quiz
    from app.services.xp_engine import calculate_xp
    from app.services.level_engine import calculate_level
    from flask_login import current_user
    from app import db

    questions = None

    if request.method == "POST":

        topic = request.form["topic"]

        questions = generate_quiz(topic)

        # Example simulated score
        score = 80

        xp = calculate_xp(score)

        current_user.xp += xp
        current_user.total_score += score
        current_user.total_quizzes += 1

        current_user.level = calculate_level(current_user.xp)

        db.session.commit()

    return render_template(
        "quiz.html",
        questions=questions
    )
