from app import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    topic = db.Column(db.String(200))
    score = db.Column(db.Integer)
    weak_area = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
