# Initialize globally used variables

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

from .config import config

app = Flask(config.APPNAME)
app.config.from_object(config)

db = SQLAlchemy(app)
db.init_app(app)

from .utils import DatabaseSessionInterface
app.session_interface = DatabaseSessionInterface(db)

loginmgr = LoginManager()
loginmgr.init_app(app)

@loginmgr.user_loader
def load_user(uid):
    from .models.user import Account
    return db.session.query(Account).get(uid)

import api

api.bps.attach(app, url_prefix='/api/')

