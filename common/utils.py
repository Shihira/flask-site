import os, re

from flask import Blueprint

def find_modules(init_file, fpattern = None):
    """
    List names of modules in the same directory as init_file. The function is
    usually used in __init__.py and returns value fit for __all__.
    If you need to import it, use __import__ with level 1.
    """

    import pkgutil

    fpattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$") \
            if fpattern is None else re.compile(fpattern)

    dirname = os.path.dirname(init_file)
    parmod = os.path.dirname(dirname)
    entries = [modname for _, modname, _ in pkgutil.iter_modules([dirname])]
    entries = list(filter(lambda n: fpattern.match(n), entries))

    return entries

def join_url(*args, **kwargs):
    """
    Join a args with seps. example:

        >>> join_url("abc/", "/def/", "fed", "yui")
        '/abc/def/fed/yui/'
        >>> join_url("abc", "def#", "##fed", "yui", sep=('^', '#', '$'))
        '^abc#def##fed#yui$'

    """
    sep = kwargs["sep"] if "sep" in kwargs else ('/', '/', '/')

    concat_str = sep[0]
    concat_str += args[0][1:] if args[0][0] == sep[0] else args[0]

    for a in args[1:]:
        concat_str += "" if concat_str[-1] == sep[1] else sep[1]
        concat_str += a[1:] if a[0][0] == sep[1] else a

    concat_str += "" if concat_str[-1] == sep[2] else sep[2]

    return concat_str

class BlueprintSet(object):
    """
    A set of blueprint which aims to simplify the operation of decoupling and
    grouping blueprints. Add blueprints to a BlueprintSet instance, followed by
    attaching the blueprint to an app with a url_prefix.
    """

    def __init__(self):
        self.blueprints = {}

    def add_blueprint(self, name, bp):
        if name in self.blueprints:
            raise KeyError("Blueprint name is duplicated.")
        else:
            if isinstance(bp, Blueprint):
                self.blueprints[name] = bp
            elif isinstance(bp, BlueprintSet):
                for (sub_name, sub_bp) in bp.blueprints.items():
                    self.blueprints[join_url(name, sub_name)] = sub_bp
                    

    def attach(self, app, url_prefix='', **options):
        for (name, bp) in self.blueprints.items():
            app.register_blueprint(bp,
                    url_prefix=join_url(url_prefix, name), **options)


################################################################################
# Request Argument Conversion and Validation

def email_type(email_str):
    if re.match("^[^@]+@[a-zA-Z0-9\-_\.]+$", email_str):
        return email_str
    else:
        raise ValueError("Not a Proper Email.")

def phone_type(phone_str):
    if re.match("^\d+$", phone_str):
        return phone_str
    else:
        raise ValueError("Not a Proper Phone Number.")

def md5_hashed_type(mhstr):
    if re.match("^[a-zA-Z0-9]{32}$", mhstr):
        return mhstr
    else:
        raise ValueError("Not MD5 Hashed.")

################################################################################
# Session Interface

import pickle
import uuid

from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from .models.session import Session

class DatabaseSession(CallbackDict, SessionMixin):
    @staticmethod
    def _update(self):
        self.modified = True

    def __init__(self, initial=None, sid=None, new=False):
        CallbackDict.__init__(self, initial, self._update)
        self.sid = sid if sid else self.get_session_id()
        self.new = new
        self.modified = False

    @staticmethod
    def get_session_id():
        return str(uuid.uuid4())

class DatabaseSessionInterface(SessionInterface):
    serializer = pickle.dumps
    unserializer = pickle.loads
    session_class = DatabaseSession
    session_table = Session

    def __init__(self, db):
        self.db = db

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            return DatabaseSession(new=True)

        session_record = self.session_table.query.get(sid)
        if not session_record:
            return DatabaseSession(sid=sid, new=True)

        initial = self.unserializer(session_record.data)
        return DatabaseSession(sid=sid, initial=initial)

    def save_session(self, app, session, response):
        from .globals import app
        from datetime import datetime

        assert isinstance(session, self.session_class)

        # cookie properties
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)

        sid = session.sid
        data = self.serializer(dict(session))
        expiry = self.get_expiration_time(app, session)

        session_record = self.session_table.query.get(sid)
        if session_record:
            session_record.data = data
            session_record.expiry = expiry
        else:
            session_record = self.session_table(
                    sid = sid,
                    data = data,
                    expiry = expiry
                )
            self.db.session.add(session_record)

        self.db.session.commit()

        response.set_cookie(app.session_cookie_name, sid, expires=expiry,
                domain=domain, path=path, httponly=httponly, secure=secure)

