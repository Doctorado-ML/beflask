#!/usr/bin/env python
import os
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_socketio import SocketIO
from .config import config
from .models import User, db

from .results.main_results import results
from .admin.main_admin import admin

from .main import main

bootstrap = Bootstrap5()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def make_shell_context():
    return {"db": db, "User": User}


def create_app(config_name=None, return_socketio=False):
    if config_name is None:
        config_name = os.environ.get("BEFLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    app.jinja_env.auto_reload = True
    app.register_blueprint(results, url_prefix="/results")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(main)
    app.shell_context_processor(make_shell_context)
    socketio = SocketIO(app)
    with app.app_context():
        db.create_all()
        app.socket = socketio
        from .interactive.main_interactive import interactive

        app.register_blueprint(interactive, url_prefix="/bench")
    if return_socketio:
        return socketio, app
    else:
        return app
