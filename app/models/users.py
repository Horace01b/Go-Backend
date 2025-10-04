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
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    games = db.relationship("Game", backref="user", lazy=True)


class Game(db.Model):
    __tablename__ = "games"


    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    captured_white = db.Column(db.Integer, nullable=False, default=0)
    captured_black = db.Column(db.Integer, nullable=False, default=0)
    scores = db.Column(db.JSON, default={"black": 0, "white": 0})
    won_by = db.Column(db.String(20), nullable=True)
    opponent_type = db.Column(db.String(20), nullable=False, default="computer") 
    board_size = db.Column(db.Integer, nullable=False, default=9)
    board_state = db.Column(db.JSON, nullable=False, default=dict)
    current_turn = db.Column(db.String(10), nullable=False, default="black")
    state = db.Column(db.String(20), nullable=False, default="ongoing")  
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True))

class Move(db.Model):
    __tablename__ = "moves"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)

    player_color = db.Column(db.String(10), nullable=False) 
    x = db.Column(db.Integer, nullable=True)   
    y = db.Column(db.Integer, nullable=True)  

    captures_black = db.Column(db.Integer, default=0)
    captures_white = db.Column(db.Integer, default=0)
    scores = db.Column(db.JSON, default={"black": 0, "white": 0})

    move_type = db.Column(db.String(20), default="play")  
    # play = stone placed, pass = skipped turn, resign = resignation

    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    game = db.relationship("Game", backref="moves")
