from app import db

class Performance(db.Model):
    __tablename__ = "performances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    topic = db.Column(db.String(200))
    average_score = db.Column(db.Float)
