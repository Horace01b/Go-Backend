from flask import Blueprint,jsonify,request,send_from_directory
from app.models import User
from app.db import db
import re
import os
from flask_bcrypt import Bcrypt

user_bp=Blueprint("user",__name__,url_prefix="/user")