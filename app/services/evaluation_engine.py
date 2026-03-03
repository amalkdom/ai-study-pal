from app.models.question import Question
from app.models.answer import Answer
from app.models.quiz import Quiz
from app import db

def evaluate_answers(user_id, quiz_id, submitted_answers):

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    score = 0

    for question in questions:
        selected = submitted_answers.get(str(question.id))
        is_correct = selected == question.correct_answer

        if is_correct:
            score += 20

        answer = Answer(
            question_id=question.id,
            user_id=user_id,
            selected_option=selected,
            is_correct=is_correct
        )
        db.session.add(answer)

    quiz = Quiz.query.get(quiz_id)
    quiz.score = score

    db.session.commit()

    return score
