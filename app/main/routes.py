from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.ai_engine import ask_ai
from app.services.analytics_engine import update_topic_performance
from app.services.evaluation_engine import evaluate_answers
from app.services.recommendation_engine import generate_recommendation
from app.models.quiz import Quiz
from app.models.performance import Performance
from app.models.ai_history import AIHistory
from app.models.question import Question
from app.models.answer import Answer
from app import db
from sqlalchemy import func
import json
from datetime import datetime

main = Blueprint("main", __name__)


# ===========================
# DASHBOARD
# ===========================
@main.route("/dashboard")
@login_required
def dashboard():

    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    performances = Performance.query.filter_by(user_id=current_user.id).all()

    scores = [q.score for q in quizzes if q.score is not None]

    total_quizzes = len(scores)
    average_score = round(sum(scores)/total_quizzes, 1) if total_quizzes > 0 else 0

    # Predictive analytics (simple trend projection)
    predicted_score = average_score + 5 if total_quizzes > 0 else 0

    # Weak topic detection
    weak_topics = [
        p.topic for p in performances if p.average_score < 60
    ]

    # Personalized recommendation
    recommendation = generate_recommendation(current_user.id)

    return render_template(
        "dashboard.html",
        scores=json.dumps(scores),
        total_quizzes=total_quizzes,
        average_score=average_score,
        predicted_score=predicted_score,
        weak_topics=weak_topics,
        recommendation=recommendation
    )


# ===========================
# STUDY PLANNER
# ===========================
@main.route("/planner", methods=["GET", "POST"])
@login_required
def planner():

    plan = None

    if request.method == "POST":
        topic = request.form["topic"]
        hours = request.form["hours"]

        prompt = f"""
        Create a structured adaptive study plan for {topic}
        for {hours} hours including revision checkpoints.
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
            flash("AI service error.")

    return render_template("planner.html", plan=plan)


# ===========================
# GENERATE QUIZ
# ===========================
@main.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    quiz = None
    questions = None
    feedback = None

    if request.method == "POST":

        topic = request.form["topic"]

        prompt = f"""
        Generate 5 MCQs in JSON format.
        Each question must contain:
        question, option_a, option_b, option_c, option_d, correct_answer.
        Topic: {topic}
        """

        try:
            response = ask_ai(prompt)
            questions_data = json.loads(response)

            quiz = Quiz(user_id=current_user.id, topic=topic, score=0)
            db.session.add(quiz)
            db.session.commit()

            for q in questions_data:
                question = Question(
                    quiz_id=quiz.id,
                    text=q["question"],
                    option_a=q["option_a"],
                    option_b=q["option_b"],
                    option_c=q["option_c"],
                    option_d=q["option_d"],
                    correct_answer=q["correct_answer"]
                )
                db.session.add(question)

            db.session.commit()

            questions = Question.query.filter_by(quiz_id=quiz.id).all()

        except Exception:
            flash("AI service error.")

    return render_template(
        "quiz.html",
        quiz=quiz,
        questions=questions,
        feedback=feedback
    )


# ===========================
# SUBMIT QUIZ
# ===========================
@main.route("/submit_quiz/<int:quiz_id>", methods=["POST"])
@login_required
def submit_quiz(quiz_id):

    submitted_answers = request.form.to_dict()

    score = evaluate_answers(current_user.id, quiz_id, submitted_answers)

    quiz = Quiz.query.get(quiz_id)
    update_topic_performance(current_user.id, quiz.topic)

    feedback = f"You scored {score}%."

    return redirect(url_for("main.dashboard"))


# ===========================
# PERFORMANCE PAGE
# ===========================
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


# ===========================
# CHATBOT
# ===========================
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
            flash("AI service error.")

    return render_template("chatbot.html", reply=reply)


# ===========================
# TIMELINE
# ===========================
@main.route("/timeline")
@login_required
def timeline():

    history = AIHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(AIHistory.created_at.desc()).all()

    return render_template("timeline.html", history=history)
