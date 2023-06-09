from app import app

socketio, app = app.create_app()
socketio.run(app, debug=True)
