from flask import Flask
from flask_socketio import SocketIO
import os

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    from . import routes
    app.register_blueprint(routes.bp)

    socketio.init_app(app)

    return app