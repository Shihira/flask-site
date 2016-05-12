from ..globals import db, app

import datetime
import uuid

class Session(db.Model):
    __tablename__ = app.config["TABLE_PREFIX"] + 'session'

    sid = db.Column(db.String(36), primary_key=True,
            default=lambda: str(uuid.uuid4()))
    data = db.Column(db.LargeBinary)
    expiry = db.Column(db.DateTime, default=lambda: \
            datetime.datetime.now() + app.config["PERMANENT_SESSION_LIFETIME"])

