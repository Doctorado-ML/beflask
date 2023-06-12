#!/usr/bin/env python
from beflask import app

socketio, app = app.create_app(return_socketio=True)
socketio.run(app, debug=app.config["DEBUG"])
