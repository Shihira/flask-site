#!/usr/bin/env python3

import os
import sys
import inspect
#import warnings

sys.path.insert(0, os.path.dirname(__file__))

#if sys.version_info > (2, 7):
#    warnings.warn("Due to few flask extentions having supported Py3k, "
#            "please check carefully if your code is fully compatible.")

# prepend project root path to module search paths

registered_command = {}

def as_command(arg=""):

    def reg(func):
        global registered_command
        true_name = arg
        if arg is "":
            true_name = func.__name__
        registered_command[true_name] = func
        return func

    return reg

################################################################################
# Commands

@as_command()
def run(port=5000):
    from common.globals import app
    app.run(port=port, debug=True)

@as_command()
def initdb(drop=False):
    from common.globals import db
    import common.models.user
    import common.models.session

    if not drop:
        db.create_all()
    else:
        db.drop_all()

@as_command()
def help(func=None):
    global registered_command

    if func is None:
        print("Available commands:")
        for ln in registered_command.keys():
            print("    " + ln)
    else:
        if func in registered_command:
            print("Arguments of %s:" % func)
            ca = inspect.getcallargs(registered_command[func])
            for k, d in ca.items():
                print("    --%s\t\t(default: %s)" % (k, repr(d)))

################################################################################

def parse_arguments(arg_list):
    args = []
    kwargs = {}

    setting_key = None

    for a in arg_list:
        if setting_key and a[:2] == "--":
            kwargs[setting_key] = True
            setting_key = None

        if setting_key is None:
            if a[:2] == "--":
                setting_key = a[2:]
            else: args += [a]
        else:
            kwargs[setting_key] = a
            setting_key = None

    if setting_key:
        kwargs[setting_key] = True
        setting_key = None

    return args, kwargs

def __main__():
    if sys.argv[1] in registered_command:
        func = registered_command[sys.argv[1]]
        args, kwargs = parse_arguments(sys.argv[2:])
        func(*args, **kwargs)
    else:
        print("No such command. Run ./admin.py help for more information.")

if __name__ == "__main__":
    __main__()

