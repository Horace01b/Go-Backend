from flask import Blueprint, jsonify, request, current_app
from flask_bcrypt import Bcrypt
from sqlalchemy import or_
import re
from flask_jwt_extended import create_access_token

from app.models import User
from app.db import db 

bcrypt = Bcrypt() 

user_bp = Blueprint("user", __name__, url_prefix="/user")

def is_valid_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def validate_password(password):
    return bool(password and len(password) >= 6)

def public_user_dict(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }
# Signup Route
@user_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "invalid email address"}), 400

    if not validate_password(password):
        return jsonify({"error": "password must be at least 6 characters"}), 400

    existing = User.query.filter(
        or_(User.name == name, User.email == email)).first()
    if existing:
        return jsonify({"error": "username or email already in use"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(name=name, email=email, password_hash=password_hash)
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to create user")
        return jsonify({"error": "internal server error"}), 500
    return jsonify({"message": "user created", "user": public_user_dict(new_user)}), 201

# Login Route
@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    login_value = (data.get("login") or data.get("name") or data.get("email") or "").strip()
    password = data.get("password") or ""

    if not login_value or not password:
        return jsonify({"error": "login and password are required"}), 400

    user = User.query.filter(
        or_(User.email == login_value, User.name == login_value)
    ).first()

    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "logged in",
        "access_token": access_token,
        "user": public_user_dict(user)
    }), 200
