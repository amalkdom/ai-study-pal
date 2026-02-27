from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import random
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
app.secret_key = "scholarai_pro_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- SAFE NLTK --------
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

# -------- DATABASE --------
def init_db():
    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS documents(
        username TEXT,
        content TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS quiz_attempts(
        username TEXT,
        score INTEGER,
        precision REAL,
        recall REAL,
        f1 REAL,
        difficulty TEXT)""")

    conn.commit()
    conn.close()

init_db()

# -------- LOGIN --------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("scholarai.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/workspace")

    return render_template("login.html")

# -------- REGISTER --------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("scholarai.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# -------- WORKSPACE --------
@app.route("/workspace", methods=["GET","POST"])
def workspace():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()

    summary = ""
    keywords = []
    quiz = []
    result = None
    difficulty = "medium"

    # -------- UPLOAD DOCUMENT --------
    if request.method == "POST":

        if "file" in request.files:
            file = request.files["file"]
            text = file.read().decode("utf-8")
            c.execute("DELETE FROM documents WHERE username=?",(username,))
            c.execute("INSERT INTO documents VALUES (?,?)",(username,text))
            conn.commit()

        # -------- GENERATE SUMMARY --------
        if "generate_summary" in request.form:
            c.execute("SELECT content FROM documents WHERE username=?",(username,))
            doc = c.fetchone()
            if doc:
                text = doc[0]
                vectorizer = TfidfVectorizer(stop_words="english",max_features=8)
                X = vectorizer.fit_transform([text])
                keywords = vectorizer.get_feature_names_out()
                summary = " ".join(text.split()[:80])

        # -------- GENERATE QUIZ --------
        if "generate_quiz" in request.form:
            c.execute("SELECT content FROM documents WHERE username=?",(username,))
            doc = c.fetchone()
            if doc:
                text = doc[0]
                words = text.split()
                sample = random.sample(words,min(5,len(words)))

                for w in sample:
                    correct = f"{w} relates to the topic"
                    options = [
                        correct,
                        f"{w} unrelated",
                        f"{w} random",
                        f"{w} meaningless"
                    ]
                    random.shuffle(options)

                    quiz.append({
                        "question":f"What best describes '{w}'?",
                        "options":options,
                        "correct":correct
                    })

                session["quiz"] = quiz

        # -------- SUBMIT QUIZ --------
        if "submit_quiz" in request.form:
            quiz = session.get("quiz",[])
            answers = request.form.getlist("answer")

            correct_count = 0
            y_true = []
            y_pred = []

            for i,q in enumerate(quiz):
                correct = q["correct"]
                y_true.append(1)
                if i < len(answers) and answers[i] == correct:
                    correct_count += 1
                    y_pred.append(1)
                else:
                    y_pred.append(0)

            total = len(quiz)
            score = int((correct_count/total)*100) if total else 0

            precision = correct_count/total if total else 0
            recall = precision
            f1 = (2*precision*recall/(precision+recall)) if precision else 0

            if score > 80:
                difficulty = "hard"
            elif score < 40:
                difficulty = "easy"
            else:
                difficulty = "medium"

            c.execute("""INSERT INTO quiz_attempts 
                         VALUES (?,?,?,?,?,?)""",
                      (username,score,precision,recall,f1,difficulty))
            conn.commit()

            result = f"You scored {score}% | F1: {round(f1,2)}"

    conn.close()

    return render_template("workspace.html",
                           summary=summary,
                           keywords=keywords,
                           quiz=quiz,
                           result=result)

# -------- ANALYTICS --------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()
    c.execute("SELECT score FROM quiz_attempts WHERE username=?",(username,))
    scores = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template("analytics.html",scores=scores)

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
