from app.db import db
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    # def set_password(self, plain_password):
    #     """Hashes and stores the password"""
    #     self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    # def check_password(self, plain_password):
    #     """Verify a password against the stored hash"""
    #     return bcrypt.check_password_hash(self.password_hash, plain_password)


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)


    captured_white = db.Column(db.Integer, nullable=False, default=0)
    captured_black = db.Column(db.Integer, nullable=False, default=0)
    scores = db.Column(db.JSON, default={"black": 0, "white": 0})
    won_by = db.Column(db.String, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    opponent_type = db.Column(db.String, nullable=False, default="computer") 

    board_size = db.Column(db.Integer, nullable=False, default=19)
    board_state = db.Column(db.JSON, nullable=False, default=dict)

    current_turn = db.Column(db.String, nullable=False, default="black")
    state = db.Column(db.String, nullable=False, default="ongoing")  

    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True))
