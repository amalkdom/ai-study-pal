from app.models.quiz import Quiz
from app.models.performance import Performance
from app import db

def update_topic_performance(user_id, topic):
    quizzes = Quiz.query.filter_by(user_id=user_id, topic=topic).all()

    if not quizzes:
        return

    avg = sum([q.score for q in quizzes]) / len(quizzes)

    performance = Performance.query.filter_by(
        user_id=user_id,
        topic=topic
    ).first()

    if performance:
        performance.average_score = avg
    else:
        performance = Performance(
            user_id=user_id,
            topic=topic,
            average_score=avg
        )
        db.session.add(performance)

    db.session.commit()
