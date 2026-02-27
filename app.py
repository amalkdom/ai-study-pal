from flask import Flask, render_template, request, redirect, session, url_for
import random

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
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if username not in user_stats:
        user_stats[username] = {"xp": 0, "score": 0}

    stats = user_stats[username]

    weak_area = "Needs More Practice"
    if stats["score"] > 3:
        weak_area = "Strong Performance"

    motivational_message = "You're making steady progress. Keep it up!"

    return render_template("dashboard.html",
                           user=username,
                           stats=stats,
                           weak_area=weak_area,
                           motivational_message=motivational_message)


# ---------------- QUIZ ----------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if username not in user_stats:
        user_stats[username] = {"xp": 0, "score": 0}

    question = ""
    result = ""

    if request.method == "POST":
        module = request.form.get("module")
        level = request.form.get("level")
        answer = request.form.get("answer")

        correct_answer = "Concept A"
        question = f"{level.capitalize()} question from module: {module}"

        if answer:
            if answer == correct_answer:
                result = "Correct!"
                user_stats[username]["xp"] += 10
                user_stats[username]["score"] += 1
            else:
                result = "Incorrect. Review the module."

    return render_template("quiz.html",
                           question=question,
                           result=result)


# ---------------- SUMMARIZER ----------------
@app.route("/summarize", methods=["GET", "POST"])
def summarize():
    if "user" not in session:
        return redirect(url_for("login"))

    summary = ""
    keywords = []
    tips = []

    if request.method == "POST":
        text = request.form.get("content")

        summary = " ".join(text.split()[:50])
        keywords = list(set(text.split()))[:5]

        tips = [
            "Review key terms daily",
            "Practice definitions twice a week",
            "Create flashcards"
        ]

    return render_template("summarize.html",
                           summary=summary,
                           keywords=keywords,
                           tips=tips)


# ---------------- PROGRESS ----------------
@app.route("/progress")
def progress():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("progress.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


