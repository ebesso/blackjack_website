from flask import Flask, render_template
from flask_socketio import SocketIO

from initializer import init_cards, init_database
from user_handler import validate_user_identifier

import configuration_handler

from user_login import user_login_bp

app = Flask(__name__)

app.secret_key = '123'
app.debug = True

init_database()
init_cards()

app.register_blueprint(user_login_bp)

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html', website_info=configuration_handler.load('website'))

@app.route('/join', methods=['POST'])
@validate_user_identifier
def join_game():
    return render_template('blackjack.html', website_info=configuration_handler('website'))

@socketio.on('connect')
@validate_client
def client_connect(data):
    print('Client has valid game session')
    socketio.emit('New-round', data=generate_hand())

@socketio.on('draw')

@socketio.on('disconnect')
@validate_client
def client_disconnect(data):
    print()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')