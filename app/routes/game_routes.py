from flask import Blueprint, jsonify, request
from app.models import Game, utc_now
from app.db import db

game_bp = Blueprint("game", __name__, url_prefix="/game")

# Temporary helper to simulate "logged-in user"
def get_current_user_id():
    # Expect user_id in request header (X-User-ID) for testing
    return request.headers.get("X-User-ID", type=int)

def get_active_game(user_id):
    return Game.query.filter_by(user_id=user_id, state="ongoing").first()

# ---------------------------
# POST /game/new
# ---------------------------
@game_bp.route("/new", methods=["POST"])
def new_game():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Missing X-User-ID header"}), 400

    # End previous active game
    active = get_active_game(user_id)
    if active:
        active.state = "abandoned"
        active.ended_at = utc_now()

    game = Game(user_id=user_id, board_state={}, current_turn="black")
    db.session.add(game)
    db.session.commit()
    return jsonify({"message": "New game started", "game_id": game.id}), 201


# ---------------------------
# GET /game/active
# ---------------------------
@game_bp.route("/active", methods=["GET"])
def active_game():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Missing X-User-ID header"}), 400

    game = get_active_game(user_id)
    if not game:
        return jsonify({"message": "No active game"}), 404

    return jsonify({
        "id": game.id,
        "board": game.board_state,
        "turn": game.current_turn,
        "scores": game.scores,
        "state": game.state,
    })


# ---------------------------
# POST /game/move
# ---------------------------
@game_bp.route("/move", methods=["POST"])
def make_move():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Missing X-User-ID header"}), 400

    data = request.get_json()
    x, y = data.get("x"), data.get("y")

    game = get_active_game(user_id)
    if not game:
        return jsonify({"error": "No active game"}), 404
    if game.state != "ongoing":
        return jsonify({"error": "Game already finished"}), 400

    # Very simplified move logic
    board = game.board_state
    board[str((x, y))] = game.current_turn
    game.current_turn = "white" if game.current_turn == "black" else "black"

    # Simulate bot move if playing vs computer
    if game.opponent_type == "computer" and game.current_turn == "white":
        board[str((0, 0))] = "white"  # always place at (0,0)
        game.current_turn = "black"

    db.session.commit()
    return jsonify({
        "board": game.board_state,
        "turn": game.current_turn,
        "scores": game.scores,
        "state": game.state,
    })


# ---------------------------
# POST /game/pass
# ---------------------------
@game_bp.route("/pass", methods=["POST"])
def pass_turn():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Missing X-User-ID header"}), 400

    game = get_active_game(user_id)
    if not game:
        return jsonify({"error": "No active game"}), 404

    passes = game.board_state.get("passes", 0) + 1
    game.board_state["passes"] = passes

    if passes >= 2:
        game.state = "finished"
        game.ended_at = utc_now()

    game.current_turn = "white" if game.current_turn == "black" else "black"
    db.session.commit()

    return jsonify({
        "board": game.board_state,
        "turn": game.current_turn,
        "state": game.state,
        "game_over": game.state == "finished",
    })


# ---------------------------
# POST /game/finish
# ---------------------------
@game_bp.route("/finish", methods=["POST"])
def finish_game():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Missing X-User-ID header"}), 400

    game = get_active_game(user_id)
    if not game:
        return jsonify({"error": "No active game"}), 404

    game.state = "finished"
    game.ended_at = utc_now()
    db.session.commit()
    return jsonify({"message": "Game finished"})



@game_bp.route("/history", methods=["GET"])
def game_history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Missing X-User-ID header"}), 400

    games = Game.query.filter_by(user_id=user_id).order_by(Game.created_at.desc()).all()

    return jsonify([{
        "id": g.id,
        "created_at": g.created_at.isoformat(),
        "ended_at": g.ended_at.isoformat() if g.ended_at else None,
        "won_by": g.won_by,
        "scores": g.scores,
        "state": g.state,
    } for g in games])








