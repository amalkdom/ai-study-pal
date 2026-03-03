import json
from app.services.ai_engine import ask_ai
from app.models.quiz import Quiz
from app.models.question import Question
from app import db

def generate_structured_quiz(user_id, topic):

    prompt = f"""
    Generate 5 MCQs in JSON format.
    Each question must contain:
    question, option_a, option_b, option_c, option_d, correct_answer.
    Topic: {topic}
    """

    response = ask_ai(prompt)

    quiz = Quiz(user_id=user_id, topic=topic, score=0)
    db.session.add(quiz)
    db.session.commit()

    questions_data = json.loads(response)

    for q in questions_data:
        question = Question(
            quiz_id=quiz.id,
            text=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"]
        )
        db.session.add(question)

    db.session.commit()

    return quiz.id
