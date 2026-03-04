from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    age = db.Column(db.Integer)
    class_level = db.Column(db.String(50))

    role = db.Column(db.String(20), default="student")

    # Learning metrics
    total_score = db.Column(db.Integer, default=0)
    total_quizzes = db.Column(db.Integer, default=0)

    # Gamification
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)

    # Performance
    average_score = db.Column(db.Integer, default=0)
    predicted_score = db.Column(db.Integer, default=0)
