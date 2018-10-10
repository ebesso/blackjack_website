from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID

import os, logging

socketio = SocketIO()
db = SQLAlchemy()
oid = OpenID()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def create_app(debug_mode):
    app = Flask(__name__)

    app.debug = debug_mode
    app.secret_key = '123abc'

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

    from others import others as others_bp
    from singleplayer import singleplayer as singleplayer_bp
    from multiplayer import multiplayer as multiplayer_bp

    app.register_blueprint(others_bp)
    app.register_blueprint(multiplayer_bp)
    app.register_blueprint(singleplayer_bp)

    socketio.init_app(app)
    db.init_app(app)
    oid.init_app(app)

    return app
    