from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.ai.services import *
from app.models.quiz import QuizResult
from app import db
import json

main = Blueprint("main", __name__)

@main.route("/dashboard")
@login_required
def dashboard():
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    scores = [r.score for r in results]
    return render_template("dashboard.html", scores=json.dumps(scores))

@main.route("/planner", methods=["GET","POST"])
@login_required
def planner():
    plan = None
    if request.method == "POST":
        plan = generate_study_plan(
            request.form["topic"],
            request.form["hours"]
        )
    return render_template("planner.html", plan=plan)

@main.route("/quiz", methods=["GET","POST"])
@login_required
def quiz():
    quiz_data = None
    if request.method == "POST":
        quiz_data = generate_quiz(
            request.form["topic"],
            request.form["notes"]
        )
        result = QuizResult(
            user_id=current_user.id,
            topic=request.form["topic"],
            score=90
        )
        db.session.add(result)
        db.session.commit()

    return render_template("quiz.html", quiz=quiz_data)

@main.route("/chatbot", methods=["GET","POST"])
@login_required
def chatbot():
    reply = None
    if request.method == "POST":
        reply = ask_ai(request.form["question"])
    return render_template("chatbot.html", reply=reply)

@main.route("/summary", methods=["GET","POST"])
@login_required
def summary():
    result = None
    if request.method == "POST":
        result = summarize_text(request.form["text"])
    return render_template("summary.html", result=result)

@main.route("/youtube", methods=["GET","POST"])
@login_required
def youtube():
    summary = None
    if request.method == "POST":
        summary = summarize_youtube(request.form["link"])
    return render_template("youtube.html", summary=summary)

@main.route("/performance")
@login_required
def performance():
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    scores = [r.score for r in results]
    return render_template("performance.html", scores=json.dumps(scores))
