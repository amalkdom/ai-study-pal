from app.models.performance import Performance

def generate_recommendation(user_id):

    weak_topics = Performance.query.filter(
        Performance.user_id == user_id,
        Performance.average_score < 60
    ).all()

    if not weak_topics:
        return "You are performing consistently well. Continue advanced revision."

    topics = [w.topic for w in weak_topics]

    return f"Focus on revising these topics: {', '.join(topics)}."
