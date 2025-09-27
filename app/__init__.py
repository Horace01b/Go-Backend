from flask import Flask
from .config import Config
from .db import db,migrate
from .models import *
from .routes import user_bp
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # initialize db
    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    app.register_blueprint(user_bp)
    # app.register_blueprint(student_bp,url_prefix="/student")

    return app