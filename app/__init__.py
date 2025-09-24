from flask import Flask
from .config import Config
from .db import db,migrate
from .models import *
from .routes import user_bp

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    # initialize db
    db.init_app(app)
    migrate.init_app(app,db)

    app.register_blueprint(user_bp)
    # app.register_blueprint(student_bp,url_prefix="/student")

    return app