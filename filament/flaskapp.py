import os, sys, importlib, ConfigParser

from fabric.api import env
from flask import Flask


def discover(module_name=None):
    app_name = None
    sys.path.insert(0, env.flask_dir)
    uwsgi_file = (os.path.join(env.flask_dir, 'filament', 'uwsgi.ini')
                  if module_name is None
                  else os.path.join(env.flask_dir, 'filament', module_name))
    if module_name is None and os.path.exists(uwsgi_file):
        with open(uwsgi_file) as f:
            conf = ConfigParser.RawConfigParser()
            conf.readfp(f)
            module_name = conf.get('uwsgi', 'module')
            app_name = conf.get('uwsgi', 'callable')
    elif module_name is None:
        sys.exit("Can't find uwsgi.ini in filament/...exiting.")

    try:
        module = importlib.import_module(module_name)
    except ImportError:
        sys.exit("Can't import Flask module...exiting.")

    if app_name is not None:
        # discover callable within module
        for x in dir(module):
            app = getattr(module, x)
            if isinstance(app, Flask):
                env.flask_app = app
                return app
        else:
            sys.exit("Can't find Flask instance...exiting.")
    else:
        try:
            app = getattr(module_name, app_name)
            if isinstance(app, Flask):
                env.flask_app = app
                return app
            else:
                raise AttributeError()
        except:
            sys.exit("Can't find Flask instance...exiting.")



