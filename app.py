from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import nltk
import random
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np

app = Flask(__name__)
app.secret_key = "scholarai_pro_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- NLTK SETUP ----------
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS documents(
        username TEXT,
        content TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS chat_history(
        username TEXT,
        message TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS quiz_attempts(
        username TEXT,
        score INTEGER,
        precision REAL,
        recall REAL,
        f1 REAL)""")

    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
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

# ---------- REGISTER ----------
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

# ---------- WORKSPACE ----------
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
    history = []

    if request.method == "POST":

        # File Upload
        if "file" in request.files:
            file = request.files["file"]
            if file.filename.endswith(".pdf"):
                path = os.path.join(UPLOAD_FOLDER,file.filename)
                file.save(path)
                reader = PyPDF2.PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            else:
                text = file.read().decode("utf-8")

            c.execute("DELETE FROM documents WHERE username=?",(username,))
            c.execute("INSERT INTO documents VALUES (?,?)",(username,text))
            conn.commit()

        # Summary + TF-IDF
        if "generate_summary" in request.form:
            c.execute("SELECT content FROM documents WHERE username=?",(username,))
            doc = c.fetchone()
            if doc:
                text = doc[0]
                vectorizer = TfidfVectorizer(stop_words="english",max_features=10)
                X = vectorizer.fit_transform([text])
                keywords = vectorizer.get_feature_names_out()
                summary = " ".join(text.split()[:80])

        # Generate Quiz
        if "generate_quiz" in request.form:
            c.execute("SELECT content FROM documents WHERE username=?",(username,))
            doc = c.fetchone()
            if doc:
                text = doc[0]
                words = nltk.word_tokenize(text.lower())
                words = [w for w in words if w.isalpha()]
                unique = list(set(words))
                sample = random.sample(unique,min(5,len(unique)))

                for w in sample:
                    correct = f"{w} relates to core study concept"
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

        # Chat
        if "chat_message" in request.form:
            msg = request.form["chat_message"]
            reply = f"AI: Based on your uploaded notes, review key terms and focus on conceptual clarity."
            c.execute("INSERT INTO chat_history VALUES (?,?)",(username,"You: "+msg))
            c.execute("INSERT INTO chat_history VALUES (?,?)",(username,reply))
            conn.commit()

    c.execute("SELECT message FROM chat_history WHERE username=?",(username,))
    history = c.fetchall()
    conn.close()

    return render_template("workspace.html",
        user=username,
        summary=summary,
        keywords=keywords,
        quiz=quiz,
        history=history)

# ---------- ANALYTICS ----------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()
    c.execute("SELECT score FROM quiz_attempts WHERE username=?",(username,))
    scores = c.fetchall()
    conn.close()

    score_values = [s[0] for s in scores]

    return render_template("analytics.html",scores=score_values)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
