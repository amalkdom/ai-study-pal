def detect_weak_topics(quiz_results):

    topic_scores = {}

    for result in quiz_results:

        topic = result["topic"]
        score = result["score"]

        if topic not in topic_scores:
            topic_scores[topic] = []

        topic_scores[topic].append(score)

    weak_topics = []

    for topic, scores in topic_scores.items():

        avg = sum(scores) / len(scores)

        if avg < 60:
            weak_topics.append(topic)

    return weak_topics
