from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Game, utc_now
from app.db import db


game_bp = Blueprint("game", __name__, url_prefix="/game")


def get_active_game(user_id):
    return Game.query.filter_by(user_id=user_id, state="ongoing").first()



@game_bp.route("/new", methods=["POST"])
@jwt_required() 
def new_game():
    user_id = int(get_jwt_identity())

    # End any previous active game
    active = get_active_game(user_id)
    if active:
        active.state = "abandoned"
        active.ended_at = utc_now()

    # Create a new game
    data = request.get_json() or {}
    game = Game(
        user_id=user_id,
        board_state=data.get("board", {}),   
        current_turn=data.get("turn", "black"), 
        scores=data.get("scores", {}),
        state="ongoing"
    )

    db.session.add(game)
    db.session.commit()

    return jsonify({"message": "New game started", "game_id": game.id}), 201



@game_bp.route("/active", methods=["GET"])
@jwt_required()
def active_game():
    user_id = int(get_jwt_identity())
    game = get_active_game(user_id)

    if not game:
        return jsonify({"message": "No active game"}), 404

    return jsonify({
        "user_id": game.user_id,
        "id": game.id,
        "board": game.board_state,
        "turn": game.current_turn,
        "scores": game.scores,
        "state": game.state,
    })


@game_bp.route("/move", methods=["POST"])
@jwt_required()
def make_move():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    game = get_active_game(user_id)
    if not game:
        return jsonify({"error": "No active game"}), 404
    if game.state != "ongoing":
        return jsonify({"error": "Game already finished"}), 400

    game.board_state = data.get("board", game.board_state)
    game.current_turn = data.get("turn", game.current_turn)
    game.scores = data.get("scores", game.scores)
    game.captured_white = data.get("captured_white", game.captured_white)
    game.captured_black = data.get("captured_black", game.captured_black)

    db.session.commit()
    return jsonify({
        "board": game.board_state,
        "turn": game.current_turn,
        "scores": game.scores,
        "captured_white": game.captured_white,
        "captured_black": game.captured_black,
        "state": game.state,
    })




@game_bp.route("/pass", methods=["POST"])
@jwt_required()
def pass_turn():
    user_id = int(get_jwt_identity())
    game = get_active_game(user_id)

    if not game:
        return jsonify({"error": "No active game"}), 404

    data = request.get_json() or {}

    
    game.board_state = data.get("board", game.board_state)
    game.current_turn = data.get("turn", game.current_turn)
    game.state = data.get("state", game.state)

    if game.state == "finished":  
        game.ended_at = utc_now()

    db.session.commit()

    return jsonify({
        "board": game.board_state,
        "turn": game.current_turn,
        "state": game.state,
        "game_over": game.state == "finished",
    })


@game_bp.route("/finish", methods=["POST"])
@jwt_required()
def finish_game():
    user_id = int(get_jwt_identity())
    game = get_active_game(user_id)

    if not game:
        return jsonify({"error": "No active game"}), 404

    data = request.get_json() or {}

    game.state = "finished"
    game.ended_at = utc_now()
    game.scores = data.get("scores", game.scores)
    game.won_by = data.get("won_by", game.won_by)

    db.session.commit()

    return jsonify({"message": "Game finished"})



@game_bp.route("/history", methods=["GET"])
@jwt_required()
def game_history():
    user_id = int(get_jwt_identity())

    
    games = Game.query.filter_by(user_id=user_id).order_by(Game.created_at.desc()).all()

    return jsonify([
        {
            "id": g.id,
            "created_at": g.created_at.isoformat(),
            "ended_at": g.ended_at.isoformat() if g.ended_at else None,
            "won_by": g.won_by,
            "scores": g.scores,
            "state": g.state,
        } for g in games
    ])


