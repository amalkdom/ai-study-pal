from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from app.services.ai_engine import ask_ai
from app.services.analytics_engine import update_topic_performance
from app.services.evaluation_engine import evaluate_quiz
from app.models.quiz import Quiz
from app.models.performance import Performance
from app.models.ai_history import AIHistory
from app import db
import json
from datetime import datetime

main = Blueprint("main", __name__)


# ---------------- DASHBOARD ----------------
@main.route("/dashboard")
@login_required
def dashboard():
    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    performances = Performance.query.filter_by(user_id=current_user.id).all()

    scores = [q.score for q in quizzes]

    total_quizzes = len(scores)
    average_score = round(sum(scores)/total_quizzes, 1) if total_quizzes > 0 else 0

    weak_topics = [
        p.topic for p in performances if p.average_score < 60
    ]

    return render_template(
        "dashboard.html",
        scores=json.dumps(scores),
        average_score=average_score,
        total_quizzes=total_quizzes,
        weak_topics=weak_topics,
        performances=performances
    )


# ---------------- AI STUDY PLANNER ----------------
@main.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    plan = None

    if request.method == "POST":
        topic = request.form["topic"]
        hours = request.form["hours"]

        prompt = f"""
        Create a structured adaptive study plan for {topic}.
        User past weaknesses: Analyze based on typical student gaps.
        Duration: {hours} hours.
        Include revision checkpoints.
        """

        try:
            plan = ask_ai(prompt)

            history = AIHistory(
                user_id=current_user.id,
                action_type="study_plan",
                prompt=prompt,
                response=plan
            )

            db.session.add(history)
            db.session.commit()

        except Exception:
            flash("AI Service Error")

    return render_template("planner.html", plan=plan)


# ---------------- ADVANCED QUIZ ----------------
@main.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    quiz_data = None
    feedback = None

    if request.method == "POST":
        topic = request.form["topic"]
        notes = request.form["notes"]

        prompt = f"""
        Generate 5 MCQs for {topic}.
        Return clear format:
        Question
        A)
        B)
        C)
        D)
        Correct Answer:
        """

        try:
            quiz_data = ask_ai(prompt)

            # Simulated scoring logic (replace with real parser later)
            score = 75

            quiz_entry = Quiz(
                user_id=current_user.id,
                topic=topic,
                score=score,
                weak_area=topic if score < 60 else None
            )

            db.session.add(quiz_entry)
            db.session.commit()

            update_topic_performance(current_user.id, topic)

            feedback = evaluate_quiz(score)

        except Exception:
            flash("AI Service Error")

    return render_template("quiz.html", quiz=quiz_data, feedback=feedback)


# ---------------- PERFORMANCE ----------------
@main.route("/performance")
@login_required
def performance():
    performances = Performance.query.filter_by(
        user_id=current_user.id
    ).all()

    topics = [p.topic for p in performances]
    averages = [p.average_score for p in performances]

    return render_template(
        "performance.html",
        topics=json.dumps(topics),
        averages=json.dumps(averages)
    )


# ---------------- AI CHATBOT ----------------
@main.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():
    reply = None

    if request.method == "POST":
        question = request.form["question"]

        try:
            reply = ask_ai(question)

            history = AIHistory(
                user_id=current_user.id,
                action_type="chat",
                prompt=question,
                response=reply
            )

            db.session.add(history)
            db.session.commit()

        except Exception:
            flash("AI Service Error")

    return render_template("chatbot.html", reply=reply)


# ---------------- LEARNING TIMELINE ----------------
@main.route("/timeline")
@login_required
def timeline():
    history = AIHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(AIHistory.created_at.desc()).all()

    return render_template("timeline.html", history=history)
