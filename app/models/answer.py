from app import db

class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    user_id = db.Column(db.Integer)
    selected_option = db.Column(db.String(10))
    is_correct = db.Column(db.Boolean)
