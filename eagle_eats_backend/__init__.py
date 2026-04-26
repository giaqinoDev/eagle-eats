import os
from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config = True) #creates Flask instance
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'eagle_eats_db.sqlite')
    )

    #Load config file for testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent = True) #load config is it exitsts, but silently handle it if missing
    else:
        app.config.from_mapping(test_config)
    
    os.makedirs(app.instance_path, exist_ok = True)

    @app.route('/home')
    def hello():
        return render_template('index.html')
    
    from . import data_base
    data_base.init_app(app)

    from . import auth
    app.register_blueprint(auth.blue_print)

    return app

