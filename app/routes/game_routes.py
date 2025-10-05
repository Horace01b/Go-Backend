from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Game,Move, utc_now
from app.db import db
# from app.models import Game, Move, utc_now


game_bp = Blueprint("game", __name__, url_prefix="/game")


def get_active_game(user_id):
    return Game.query.filter_by(user_id=user_id, state="ongoing").first()



@game_bp.route("/new", methods=["POST"])
@jwt_required() 
def new_game():
    user_id = int(get_jwt_identity())

    active = get_active_game(user_id)
    if active:
        active.state = "abandoned"
        active.ended_at = utc_now()

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
    print("New game has begun")

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
    print("resume a game")


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

    # --- Update the current game 
    game.board_state = data.get("board", game.board_state)
    game.current_turn = data.get("turn", game.current_turn)
    game.scores = data.get("scores", game.scores)
    game.captured_white = data.get("captured_white", game.captured_white)
    game.captured_black = data.get("captured_black", game.captured_black)

    move = Move(
        game_id=game.id,
        player_color=data.get("color"),       
        x=data.get("x"),
        y=data.get("y"),
        move_type="play",                     
        captures_black=game.captured_black,
        captures_white=game.captured_white,
        scores=game.scores,
    )

    db.session.add(move)
    db.session.commit()  
    print(f"Saved move for game {game.id}, player {move.player_color} at ({move.x}, {move.y})")

    return jsonify({
        "message": "Move recorded successfully",
        "board": game.board_state,
        "turn": game.current_turn,
        "scores": game.scores,
        "captured_white": game.captured_white,
        "captured_black": game.captured_black,
        "state": game.state,
    }), 200




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

    move = Move(
        game_id=game.id,
        player_color=data.get("color"), 
        x=None,
        y=None,
        captures_black=game.captured_black,
        captures_white=game.captured_white,
        scores=game.scores,
        move_type="pass"
    )

    db.session.add(move)
    db.session.commit()
    print("i have passed")

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

    if data.get("resign"):
        move = Move(
            game_id=game.id,
            player_color=data.get("resign"), 
            move_type="resign",
            captures_black=game.captured_black,
            captures_white=game.captured_white,
            scores=game.scores,
        )
        db.session.add(move)

    db.session.commit()
    return jsonify({"message": "Game finished"})


@game_bp.route("/history/<int:game_id>", methods=["GET"])
@jwt_required()
def game_moves(game_id):
    user_id = int(get_jwt_identity())
    game = Game.query.filter_by(id=game_id, user_id=user_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404

    moves = [
        {
            "id": m.id,
            "player": m.player_color,
            "x": m.x,
            "y": m.y,
            "move_type": m.move_type,
            "captures_black": m.captures_black,
            "captures_white": m.captures_white,
            "scores": m.scores,
            "created_at": m.created_at.isoformat(),
        } for m in game.moves
    ]

    return jsonify({
        "game_id": game.id,
        "state": game.state,
        "moves": moves
    })
