from flask import Flask, render_template, request, redirect, session, url_for
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.secret_key = "scholarai_secret"

users = {}
user_stats = {}

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users[username] = password
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if username not in user_stats:
        user_stats[username] = {
            "xp": 0,
            "score": 0,
            "quiz_history": [],
            "concept_mistakes": {},
            "precision": 0,
            "recall": 0,
            "f1": 0,
            "difficulty_level": "medium"
        }

    stats = user_stats[username]

    return render_template("dashboard.html",
                           user=username,
                           stats=stats)

# ---------------- QUIZ ----------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    stats = user_stats[username]

    questions = []
    result = None
    explanations = []

    if request.method == "POST":

        notes = request.form.get("notes")
        submitted_answers = request.form.getlist("answer")

        # GENERATE QUESTIONS
        if notes:
            words = word_tokenize(notes.lower())
            words = [w for w in words if w.isalnum()]
            filtered = [w for w in words if w not in stopwords.words('english')]

            freq = Counter(filtered)
            keywords = [word for word, count in freq.most_common(5)]

            for word in keywords[:5]:

                if stats["difficulty_level"] == "easy":
                    correct = f"{word} is a basic concept"
                elif stats["difficulty_level"] == "hard":
                    correct = f"{word} relates to advanced analysis"
                else:
                    correct = f"{word} is an important concept"

                options = [
                    correct,
                    f"{word} is unrelated",
                    f"{word} is random",
                    f"{word} has no relevance"
                ]

                random.shuffle(options)

                questions.append({
                    "question": f"What is the meaning of '{word}'?",
                    "options": options,
                    "correct": correct
                })

            session["quiz_questions"] = questions

        # EVALUATE
        elif submitted_answers:
            questions = session.get("quiz_questions", [])
            correct_count = 0

            for i, answer in enumerate(submitted_answers):
                correct = questions[i]["correct"]
                concept = questions[i]["question"]

                if answer == correct:
                    correct_count += 1
                    explanations.append("Correct. Good understanding.")
                else:
                    explanations.append(f"Incorrect. Correct answer: {correct}")

                    if concept not in stats["concept_mistakes"]:
                        stats["concept_mistakes"][concept] = 1
                    else:
                        stats["concept_mistakes"][concept] += 1

            total = len(questions)
            score_percentage = int((correct_count / total) * 100)

            stats["xp"] += correct_count * 10
            stats["score"] += correct_count
            stats["quiz_history"].append(score_percentage)

            precision = correct_count / total if total else 0
            recall = precision
            f1 = (2 * precision * recall) / (precision + recall) if precision else 0

            stats["precision"] = round(precision, 2)
            stats["recall"] = round(recall, 2)
            stats["f1"] = round(f1, 2)

            if score_percentage > 80:
                stats["difficulty_level"] = "hard"
            elif score_percentage < 40:
                stats["difficulty_level"] = "easy"
            else:
                stats["difficulty_level"] = "medium"

            result = f"You scored {score_percentage}%"

    return render_template("quiz.html",
                           questions=questions,
                           result=result,
                           explanations=explanations,
                           difficulty=stats["difficulty_level"])

# ---------------- PROGRESS ----------------
@app.route("/progress")
def progress():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    stats = user_stats[username]

    return render_template("progress.html", stats=stats)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
