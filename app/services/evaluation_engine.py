def evaluate_quiz(score):
    if score >= 80:
        return "Excellent understanding"
    elif score >= 60:
        return "Good but needs refinement"
    else:
        return "Needs focused revision"
