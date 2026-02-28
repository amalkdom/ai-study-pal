from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
import openai
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

openai.api_key = "YOUR_OPENAI_API_KEY"

# ---------------- DATABASE ----------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    student_class = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    topic = db.Column(db.String(200))
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- AUTH ----------------

@app.route('/')
def login_page():
    return render_template("login.html")

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"])
        user = User(
            name=request.form["name"],
            age=request.form["age"],
            student_class=request.form["class"],
            email=request.form["email"],
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login_page"))
    return render_template("register.html")

@app.route('/login', methods=["POST"])
def login():
    user = User.query.filter_by(email=request.form["email"]).first()
    if user and check_password_hash(user.password, request.form["password"]):
        login_user(user)
        return redirect(url_for("dashboard"))
    flash("Invalid credentials")
    return redirect(url_for("login_page"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))

# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
@login_required
def dashboard():
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    scores = [r.score for r in results]
    return render_template("dashboard.html", scores=json.dumps(scores))

# ---------------- AI FUNCTIONS ----------------

def ask_ai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}]
    )
    return response['choices'][0]['message']['content']

# ---------------- STUDY PLANNER ----------------

@app.route('/planner', methods=["GET","POST"])
@login_required
def planner():
    plan = None
    if request.method == "POST":
        topic = request.form["topic"]
        hours = request.form["hours"]
        prompt = f"Create a professional Pomodoro-based study plan for {topic} for {hours} hours including focused sessions and breaks."
        plan = ask_ai(prompt)
    return render_template("planner.html", plan=plan)

# ---------------- QUIZ ----------------

@app.route('/quiz', methods=["GET","POST"])
@login_required
def quiz():
    quiz = None
    feedback = None

    if request.method == "POST":
        topic = request.form["topic"]
        notes = request.form["notes"]

        prompt = f"""
        Generate 5 professional MCQ questions with 4 options each and provide correct answers.
        Topic: {topic}
        Notes: {notes}
        """

        quiz = ask_ai(prompt)

        score = 85  # placeholder scoring
        result = QuizResult(user_id=current_user.id, topic=topic, score=score)
        db.session.add(result)
        db.session.commit()

        feedback = f"You scored {score}%. Strong performance."

    return render_template("quiz.html", quiz=quiz, feedback=feedback)

# ---------------- CHATBOT ----------------

@app.route('/chatbot', methods=["GET","POST"])
@login_required
def chatbot():
    reply = None
    if request.method == "POST":
        question = request.form["question"]
        reply = ask_ai(question)
    return render_template("chatbot.html", reply=reply)

# ---------------- SUMMARY ----------------

@app.route('/summary', methods=["GET","POST"])
@login_required
def summary():
    result = None
    if request.method == "POST":
        text = request.form["text"]
        prompt = f"Summarize this in structured academic format:\n{text}"
        result = ask_ai(prompt)
    return render_template("summary.html", result=result)

# ---------------- YOUTUBE ----------------

@app.route('/youtube', methods=["GET","POST"])
@login_required
def youtube():
    summary = None
    if request.method == "POST":
        link = request.form["link"]
        video_id = link.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([x["text"] for x in transcript])
        summary = ask_ai(f"Summarize this YouTube lecture:\n{text}")
    return render_template("youtube.html", summary=summary)

# ---------------- PERFORMANCE ----------------

@app.route('/performance')
@login_required
def performance():
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    scores = [r.score for r in results]
    return render_template("performance.html", scores=json.dumps(scores))

# ---------------- RUN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
