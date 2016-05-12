import importlib

import flask
import flask_restful as restful

from common.utils import find_modules
from common.error import errors_dict

blueprint = flask.Blueprint("auth", __name__)
api = restful.Api(blueprint, errors=errors_dict)

for pkgname in find_modules(__file__):
    if pkgname == "tests": continue

    submod = importlib.import_module("." + pkgname, __name__)
    if hasattr(submod, "Entry"):
        api.add_resource(submod.Entry, pkgname)

