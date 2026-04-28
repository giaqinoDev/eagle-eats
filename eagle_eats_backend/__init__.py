import os
from flask import Flask, render_template
from jinja2 import Environment
from lucide.jinja import lucide


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config = True) #creates Flask instance
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'eagle_eats_db.sqlite')
    )
    #Initiate lucide icon use for jinja
    app.jinja_env.globals.update(lucide=lucide)
    #Load config file for testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent = True) #load config is it exitsts, but silently handle it if missing
    else:
        app.config.from_mapping(test_config)
    
    os.makedirs(app.instance_path, exist_ok = True)
    
    from . import data_base
    data_base.init_app(app)

    from . import auth
    app.register_blueprint(auth.blue_print)

    from . import user
    app.register_blueprint(user.blue_print)

    from . import driver
    app.register_blueprint(driver.blue_print)

    from . import admin
    app.register_blueprint(admin.blue_print)

    from . import kitchen
    app.register_blueprint(kitchen.blue_print)


    return app

