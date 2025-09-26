# app/user.py
from flask import Blueprint, jsonify, request, current_app, session
from flask_bcrypt import Bcrypt
from sqlalchemy import or_
import re

from app.models import User   # your SQLAlchemy User model
from app.db import db         # your SQLAlchemy db instance

bcrypt = Bcrypt()  # init_app(app) recommended in your factory

user_bp = Blueprint("user", __name__, url_prefix="/user")


# ---- helpers ----
EMAIL_RE = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')


def is_valid_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email))


def validate_password(password: str) -> bool:
    # simple rule: at least 6 chars — change as you need
    return bool(password and len(password) >= 6)


def public_user_dict(user: User) -> dict:
    """Return a safe serializable user representation."""
    return {"id": user.id, "username": getattr(user, "username", None), "email": getattr(user, "email", None)}


# ---- signup ----
@user_bp.route("/signup", methods=["POST"])
def signup():
    """
    POST JSON:
    {
      "name": "player1",
      "email": "player1@example.com",
      "password": "secret123"
    }
    """
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "invalid email address"}), 400

    if not validate_password(password):
        return jsonify({"error": "password must be at least 6 characters"}), 400

    # check uniqueness
    existing = User.query.filter(or_(User.name == name, User.email == email)).first()
    if existing:
        return jsonify({"error": "username or email already in use"}), 400

    # hash password and create user
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, password_hash=password_hash)

    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to create user")
        return jsonify({"error": "internal server error"}), 500

    # optionally set session
    session["user_id"] = user.id

    return jsonify({"message": "user created", "user": public_user_dict(user)}), 201


# ---- login ----
@user_bp.route("/login", methods=["POST"])
def login():
    """
    POST JSON:
    {
      "login": "player1"   # or "email"
      "password": "secret123"
    }
    """
    data = request.get_json() or {}
    login_value = (data.get("login") or data.get("username") or data.get("email") or "").strip()
    password = data.get("password") or ""

    if not login_value or not password:
        return jsonify({"error": "login and password are required"}), 400

    # try by email then username
    user = User.query.filter(
        or_(User.email == login_value, User.username == login_value)
    ).first()

    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    # ensure the model stores password_hash in this attribute name
    if not getattr(user, "password_hash", None):
        return jsonify({"error": "user has no password set"}), 500

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    # login success
    session["user_id"] = user.id
    return jsonify({"message": "logged in", "user": public_user_dict(user)}), 200
