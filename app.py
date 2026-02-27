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
        user_stats[username] = {
            "xp": 0,
            "score": 0,
            "quiz_history": []
        }

    questions = []
    result = None
    explanations = []
    difficulty = "medium"

    if request.method == "POST":

        notes = request.form.get("notes")
        difficulty = request.form.get("difficulty")
        submitted_answers = request.form.getlist("answer")

        # ---------------- GENERATE QUESTIONS ----------------
        if notes:
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter

            words = word_tokenize(notes.lower())
            words = [w for w in words if w.isalnum()]
            filtered = [w for w in words if w not in stopwords.words('english')]

            freq = Counter(filtered)
            keywords = [word for word, count in freq.most_common(5)]

            for word in keywords[:5]:
                if difficulty == "easy":
                    correct = f"{word} is a basic concept"
                elif difficulty == "hard":
                    correct = f"{word} relates to advanced analysis"
                else:
                    correct = f"{word} is an important concept"

                options = [
                    correct,
                    f"{word} is unrelated",
                    f"{word} is a random term",
                    f"{word} has no meaning"
                ]

                random.shuffle(options)

                questions.append({
                    "question": f"What is the meaning of '{word}'?",
                    "options": options,
                    "correct": correct
                })

            session["quiz_questions"] = questions

        # ---------------- EVALUATE ANSWERS ----------------
        elif submitted_answers:
            questions = session.get("quiz_questions", [])
            correct_count = 0

            for i, answer in enumerate(submitted_answers):
                correct = questions[i]["correct"]
                if answer == correct:
                    correct_count += 1
                    explanations.append("Correct. Good understanding.")
                else:
                    explanations.append(
                        f"Incorrect. Correct answer: {correct}"
                    )

            score_percentage = int((correct_count / len(questions)) * 100)

            user_stats[username]["xp"] += correct_count * 10
            user_stats[username]["score"] += correct_count

            user_stats[username]["quiz_history"].append(score_percentage)

            result = f"You scored {score_percentage}%"

    return render_template(
        "quiz.html",
        questions=questions,
        result=result,
        explanations=explanations,
        difficulty=difficulty
    )

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




