from flask import Flask, render_template, request, redirect, session, url_for
import random

app = Flask(__name__)
app.secret_key = "scholarai_secret_key"

# Temporary in-memory user storage (Demo only)
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
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return render_template("register.html", error="User already exists")

        users[username] = password
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=session["user"])


# ---------------- SMART TUTOR ----------------
@app.route("/tutor", methods=["GET", "POST"])
def tutor():
    if "user" not in session:
        return redirect(url_for("login"))

    response = ""
    if request.method == "POST":
        question = request.form.get("question")
        response = f"Here's a simplified explanation for: {question}"

    return render_template("tutor.html", response=response)


# ---------------- STUDY PLANNER ----------------
@app.route("/planner", methods=["GET", "POST"])
def planner():
    if "user" not in session:
        return redirect(url_for("login"))

    plan = []
    if request.method == "POST":
        subject = request.form.get("subject")
        hours = request.form.get("hours")

        if subject and hours:
            try:
                hours = int(hours)
                plan = [f"Hour {i}: Study {subject}" for i in range(1, hours + 1)]
            except:
                plan = ["Invalid input"]

    return render_template("planner.html", plan=plan)


# ---------------- QUIZ ----------------
# ---------------- ADVANCED QUIZ SYSTEM ----------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if username not in user_stats:
        user_stats[username] = {"xp": 0, "score": 0}

    questions = []
    result = ""
    module = ""
    level = ""

    if request.method == "POST":
        module = request.form.get("module")
        level = request.form.get("level")
        answer = request.form.get("answer")

        if level == "easy":
            questions = [
                {"q": f"What is {module}?", "options": ["Basic Concept", "Advanced Theory", "Unrelated Topic"], "correct": "Basic Concept"}
            ]
        elif level == "medium":
            questions = [
                {"q": f"Explain core idea of {module}", "options": ["Key Principle", "Random Guess", "Wrong Idea"], "correct": "Key Principle"}
            ]
        elif level == "hard":
            questions = [
                {"q": f"Advanced application of {module}?", "options": ["Complex Analysis", "Simple Definition", "Irrelevant"], "correct": "Complex Analysis"}
            ]

        if answer:
            if answer == questions[0]["correct"]:
                result = "✅ Correct!"
                user_stats[username]["xp"] += 10
                user_stats[username]["score"] += 1
            else:
                result = "❌ Wrong! Review concept."

    return render_template("quiz.html",
                           questions=questions,
                           result=result,
                           stats=user_stats[username])
# ---------------- QUIZ WITH LEVELS ----------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))

    questions = []
    level = ""
    module = ""

    if request.method == "POST":
        level = request.form.get("level")
        module = request.form.get("module")

        if level == "easy":
            questions = [
                f"What is the basic concept of {module}?",
                f"Define {module}.",
                f"List one example of {module}."
            ]
        elif level == "medium":
            questions = [
                f"Explain how {module} works.",
                f"Describe key components of {module}.",
                f"Why is {module} important?"
            ]
        elif level == "hard":
            questions = [
                f"Analyze advanced applications of {module}.",
                f"Compare different approaches in {module}.",
                f"Solve a complex problem related to {module}."
            ]

    return render_template("quiz.html",
                           questions=questions,
                           level=level,
                           module=module)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



