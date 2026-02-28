from app import db
from datetime import datetime

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    topic = db.Column(db.String(200))
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
