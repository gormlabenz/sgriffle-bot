from app import db


class User(db.Model):
    id = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False,
                          unique=True, primary_key=True)
