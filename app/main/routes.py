from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from app.ai.services import (
    generate_study_plan,
    generate_quiz,
    summarize_text,
    summarize_youtube,
    ask_ai
)
from app.models.quiz import QuizResult
from app import db
import json

main = Blueprint(
    "main",
    __name__,
    template_folder="../templates"
)

# ---------------- DASHBOARD ----------------

@main.route("/dashboard")
@login_required
def dashboard():
    results = QuizResult.query.filter_by(
        user_id=current_user.id
    ).all()

    scores = [r.score for r in results]

    return render_template(
        "dashboard.html",
        scores=json.dumps(scores)
    )


# ---------------- STUDY PLANNER ----------------

@main.route("/planner", methods=["GET", "POST"])
@login_required
def planner():

    plan = None

    if request.method == "POST":
        topic = request.form["topic"]
        hours = request.form["hours"]

        try:
            plan = generate_study_plan(topic, hours)
        except Exception:
            flash("AI service error. Try again.")

    return render_template("planner.html", plan=plan)


# ---------------- QUIZ ----------------

@main.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    quiz_data = None
    feedback = None

    if request.method == "POST":

        topic = request.form["topic"]
        notes = request.form["notes"]

        try:
            quiz_data = generate_quiz(topic, notes)

            # For now simple scoring logic
            score = 90

            result = QuizResult(
                user_id=current_user.id,
                topic=topic,
                score=score
            )

            db.session.add(result)
            db.session.commit()

            feedback = f"You scored {score}%. Strong performance."

        except Exception:
            flash("AI service error. Try again.")

    return render_template(
        "quiz.html",
        quiz=quiz_data,
        feedback=feedback
    )


# ---------------- CHATBOT ----------------

@main.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():

    reply = None

    if request.method == "POST":
        question = request.form["question"]

        try:
            reply = ask_ai(question)
        except Exception:
            flash("AI service error.")

    return render_template("chatbot.html", reply=reply)


# ---------------- TEXT SUMMARY ----------------

@main.route("/summary", methods=["GET", "POST"])
@login_required
def summary():

    result = None

    if request.method == "POST":
        text = request.form["text"]

        try:
            result = summarize_text(text)
        except Exception:
            flash("AI service error.")

    return render_template("summary.html", result=result)


# ---------------- YOUTUBE SUMMARY ----------------

@main.route("/youtube", methods=["GET", "POST"])
@login_required
def youtube():

    summary = None

    if request.method == "POST":
        link = request.form["link"]

        try:
            summary = summarize_youtube(link)
        except Exception:
            flash("Invalid YouTube link or AI error.")

    return render_template("youtube.html", summary=summary)


# ---------------- PERFORMANCE ----------------

@main.route("/performance")
@login_required
def performance():

    results = QuizResult.query.filter_by(
        user_id=current_user.id
    ).all()

    scores = [r.score for r in results]

    return render_template(
        "performance.html",
        scores=json.dumps(scores)
    )
