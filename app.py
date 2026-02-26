from flask import Flask, render_template, request, redirect, session, url_for
import random

app = Flask(__name__)
app.secret_key = "scholarai_secret_key"

# Temporary in-memory user storage (Demo only)
users = {}

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
@app.route("/quiz")
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))

    questions = [
        "What is Newton's First Law?",
        "Explain Photosynthesis.",
        "Define Artificial Intelligence.",
        "What is a derivative in calculus?",
        "What is Object-Oriented Programming?"
    ]

    return render_template("quiz.html", questions=random.sample(questions, 3))


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
