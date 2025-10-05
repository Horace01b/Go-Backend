import os
from dotenv import load_dotenv

# loading environmental variables

load_dotenv()
# print("ENV Credentials")
# print(os.getenv("DATABASE_URL"))

class Config:
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # remove psycopg2 prepared statements
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"prepare_threshold": None},  # disables prepared statements
        "pool_pre_ping": True,                        # avoids stale connections
        "pool_recycle": 1800,                         # refresh pool every 30 mins
        "pool_size": 2,                               # small pool (Supabase friendly)
        "max_overflow": 0,
    }