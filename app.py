from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.secret_key = "scholarai_secret"

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS stats
                 (username TEXT PRIMARY KEY,
                  xp INTEGER,
                  score INTEGER,
                  difficulty TEXT,
                  precision REAL,
                  recall REAL,
                  f1 REAL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS quiz_history
                 (username TEXT, score INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (username TEXT, message TEXT)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
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
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("scholarai.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users VALUES (?,?)",
                  (username,password))
        c.execute("INSERT OR IGNORE INTO stats VALUES (?,?,?,?,?,?,?)",
                  (username,0,0,"medium",0,0,0))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()
    c.execute("SELECT xp,score,difficulty,precision,recall,f1 FROM stats WHERE username=?",(username,))
    stats = c.fetchone()
    conn.close()

    stats_dict = {
        "xp":stats[0],
        "score":stats[1],
        "difficulty":stats[2],
        "precision":stats[3],
        "recall":stats[4],
        "f1":stats[5]
    }

    return render_template("dashboard.html",
                           user=username,
                           stats=stats_dict)

# ---------------- AI CHAT ----------------
@app.route("/chat", methods=["GET","POST"])
def chat():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    response = None

    conn = sqlite3.connect("scholarai.db")
    c = conn.cursor()

    if request.method == "POST":
        message = request.form["message"]

        ai_reply = f"AI Response: Based on your query about '{message}', review core concepts carefully."

        c.execute("INSERT INTO chat_history VALUES (?,?)",(username,"You: "+message))
        c.execute("INSERT INTO chat_history VALUES (?,?)",(username,"AI: "+ai_reply))
        conn.commit()

        response = ai_reply

    c.execute("SELECT message FROM chat_history WHERE username=?",(username,))
    history = c.fetchall()
    conn.close()

    return render_template("chat.html",
                           history=history,
                           response=response)

# ---------------- SMART NOTES ----------------
@app.route("/notes", methods=["GET","POST"])
def notes():
    if "user" not in session:
        return redirect("/")

    summary = ""
    keywords = []

    if request.method == "POST":
        text = request.form["content"]

        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum()]
        filtered = [w for w in words if w not in stopwords.words('english')]

        freq = Counter(filtered)
        keywords = [word for word,count in freq.most_common(8)]
        summary = " ".join(text.split()[:50])

    return render_template("notes.html",
                           summary=summary,
                           keywords=keywords)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")
