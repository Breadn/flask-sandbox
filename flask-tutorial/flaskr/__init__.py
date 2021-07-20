# indicates dir as py package + contains app factory

import os
from flask import (Flask, redirect, url_for)

# Application factory function
def create_app(test_config=None):
    # Flask app constructor
    app = Flask(__name__, instance_relative_config=True)
    # Configure app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # Load instance config if test_config not specified
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Else, load test_config if specified
        app.config.from_mapping(test_config)
    
    # Check if instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    # Register sqlite databasea
    from . import db
    db.init_app(app)

    # Register auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # Register blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # Register user blueprint
    from . import user
    app.register_blueprint(user.bp)


    return app
