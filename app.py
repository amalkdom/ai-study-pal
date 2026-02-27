from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

app = Flask(__name__)
app.secret_key = "scholarai_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- SAFE NLTK LOAD --------
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')

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

    c.execute("""CREATE TABLE IF NOT EXISTS chat_history(
                 username TEXT,
                 message TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS quiz_history(
                 username TEXT,
                 score INTEGER)""")

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
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username,password))
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
        c.execute("INSERT OR IGNORE INTO users VALUES (?,?)",
                  (username,password))
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
    quiz_questions = []
    chat_reply = None

    # Upload text
    if request.method == "POST":

        if "document" in request.form:
            text = request.form["document"]
            c.execute("DELETE FROM documents WHERE username=?", (username,))
            c.execute("INSERT INTO documents VALUES (?,?)",(username,text))
            conn.commit()

        if "chat_message" in request.form:
            msg = request.form["chat_message"]
            c.execute("INSERT INTO chat_history VALUES (?,?)",
                      (username,"You: "+msg))

            reply = f"AI: Based on your document context, review the core ideas carefully."
            c.execute("INSERT INTO chat_history VALUES (?,?)",
                      (username,reply))
            conn.commit()
            chat_reply = reply

        if "generate_summary" in request.form:
            c.execute("SELECT content FROM documents WHERE username=?",(username,))
            doc = c.fetchone()
            if doc:
                text = doc[0]
                words = word_tokenize(text.lower())
                words = [w for w in words if w.isalnum()]
                filtered = [w for w in words if w not in stopwords.words('english')]
                freq = Counter(filtered)
                keywords = [w for w,_ in freq.most_common(8)]
                summary = " ".join(text.split()[:60])

        if "generate_quiz" in request.form:
            c.execute("SELECT content FROM documents WHERE username=?",(username,))
            doc = c.fetchone()
            if doc:
                text = doc[0]
                words = word_tokenize(text.lower())
                words = [w for w in words if w.isalnum()]
                filtered = [w for w in words if w not in stopwords.words('english')]
                freq = Counter(filtered)
                top = [w for w,_ in freq.most_common(5)]

                for word in top:
                    correct = f"{word} is an important concept"
                    options = [
                        correct,
                        f"{word} is unrelated",
                        f"{word} is random",
                        f"{word} has no meaning"
                    ]
                    random.shuffle(options)
                    quiz_questions.append({
                        "question":f"What is '{word}'?",
                        "options":options,
                        "correct":correct
                    })

    c.execute("SELECT message FROM chat_history WHERE username=?",(username,))
    history = c.fetchall()

    conn.close()

    return render_template("workspace.html",
                           user=username,
                           summary=summary,
                           keywords=keywords,
                           quiz_questions=quiz_questions,
                           history=history)
    
# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")
