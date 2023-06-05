#!/usr/bin/env python
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from .config import Config
from .models import User, db

from .results.main_select import results
from .main import main

bootstrap = Bootstrap5()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def make_shell_context():
    return {"db": db, "User": User}


def create_app():
    app = Flask(__name__)
    bootstrap.init_app(app)
    # app.register_blueprint(results)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    app.jinja_env.auto_reload = True
    app.register_blueprint(results, url_prefix="/results")
    app.register_blueprint(main)
    app.shell_context_processor(make_shell_context)
    with app.app_context():
        db.create_all()
    return app
