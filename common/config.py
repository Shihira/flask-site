from os import path
from datetime import timedelta

class ApiConfig:
    APPNAME = "assoplat"
    TABLE_PREFIX = "geek_"
    SECRET_KEY = "Too Young Too Simple, Sometimes Naive"

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ApiDebugConfig(ApiConfig):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://test:test@localhost/assoplat'
    SQLALCHEMY_ECHO = True

config = ApiDebugConfig()

