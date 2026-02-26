from flask import Flask, render_template, request
import random

app = Flask(__name__)

def generate_plan(subject, hours):
    return [f"Hour {i}: Study {subject}" for i in range(1, hours+1)]

def generate_quiz(subject):
    questions = [
        f"What is an important concept in {subject}?",
        f"Explain a key idea in {subject}.",
        f"Why is {subject} useful for students?"
    ]
    return random.sample(questions, 3)

def generate_tip(subject):
    return f"Practice {subject} daily and revise important concepts regularly."

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        subject = request.form["subject"]
        hours = int(request.form["hours"])

        plan = generate_plan(subject, hours)
        quiz = generate_quiz(subject)
        tip = generate_tip(subject)

        return render_template("result.html",
                               subject=subject,
                               plan=plan,
                               quiz=quiz,
                               tip=tip)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)