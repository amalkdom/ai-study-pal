from flask import Flask, render_template, request, redirect, session, url_for
import random

app = Flask(__name__)
app.secret_key = "scholarai_secret"

# Demo in-memory storage
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
        else:
            return render_template("login.html")

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

    return render_template("dashboard.html",
                           user=username,
                           stats=stats,
                           weak_area=weak_area)


# ---------------- QUIZ ----------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if username not in user_stats:
        user_stats[username] = {"xp": 0, "score": 0}

    questions = []
    result = ""

    if request.method == "POST":
        module = request.form.get("module")
        level = request.form.get("level")
        answer = request.form.get("answer")

        if level == "easy":
            correct = "Basic Concept"
        elif level == "medium":
            correct = "Key Principle"
        else:
            correct = "Complex Analysis"

        questions = [{
            "q": f"Question about {module}",
            "options": ["Basic Concept", "Key Principle", "Complex Analysis"],
            "correct": correct
        }]

        if answer:
            if answer == correct:
                result = "Correct!"
                user_stats[username]["xp"] += 10
                user_stats[username]["score"] += 1
            else:
                result = "Wrong!"

    return render_template("quiz.html",
                           questions=questions,
                           result=result,
                           stats=user_stats[username])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
