from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# ===========================
# DATABASE MODEL
# ===========================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.Date)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===========================
# HOME
# ===========================

@app.route('/')
def home():
    return render_template('login.html')

# ===========================
# REGISTER
# ===========================

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html')

# ===========================
# LOGIN
# ===========================

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and user.password == request.form['password']:
        login_user(user)

        today = datetime.date.today()
        if user.last_login != today:
            user.streak += 1
            user.last_login = today
            db.session.commit()

        return redirect(url_for('dashboard'))
    flash("Invalid credentials")
    return redirect(url_for('home'))

# ===========================
# DASHBOARD
# ===========================

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', streak=current_user.streak)

# ===========================
# AI QUIZ
# ===========================

@app.route('/quiz', methods=['GET','POST'])
@login_required
def quiz():
    result = None
    if request.method == 'POST':
        topic = request.form['topic']
        prompt = f"Generate 5 multiple choice quiz questions on {topic}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}]
        )
        result = response['choices'][0]['message']['content']
    return render_template('quiz.html', result=result)

# ===========================
# AI CHATBOT
# ===========================

@app.route('/chatbot', methods=['GET','POST'])
@login_required
def chatbot():
    reply = None
    if request.method == 'POST':
        doubt = request.form['doubt']
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":doubt}]
        )
        reply = response['choices'][0]['message']['content']
    return render_template('chatbot.html', reply=reply)

# ===========================
# NOTES TO QUIZ
# ===========================

@app.route('/notes', methods=['GET','POST'])
@login_required
def notes():
    quiz = None
    if request.method == 'POST':
        notes_text = request.form['notes']
        prompt = f"Create quiz from this text:\n{notes_text}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}]
        )
        quiz = response['choices'][0]['message']['content']
    return render_template('notes.html', quiz=quiz)

# ===========================
# YOUTUBE SUMMARY
# ===========================

@app.route('/youtube', methods=['GET','POST'])
@login_required
def youtube():
    summary = None
    if request.method == 'POST':
        link = request.form['link']
        video_id = link.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([x['text'] for x in transcript])

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":f"Summarize this:\n{text}"}]
        )
        summary = response['choices'][0]['message']['content']
    return render_template('youtube.html', summary=summary)

# ===========================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
