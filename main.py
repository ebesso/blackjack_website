from flask import Flask, render_template, request
from flask_socketio import SocketIO

from initializer import init_cards, init_database

from user_handler import validate_user_identifier, validate_client
from game_handler import init_game, update_table, get_cpu_identifier, update_table, isGameOver, finish_game, simulate_cpu, doubledown_valid, reset_session
from balance_handler import double_bet, sufficent_funds, current_bet, payout_bet
import deck_handler

import configuration_handler

from models import Status, Game_state

from user_login import user_login_bp

import json

app = Flask(__name__)

app.secret_key = '123'
app.debug = True

init_database()
init_cards()

app.register_blueprint(user_login_bp)

socketio = SocketIO(app)
@app.teardown_request
def remove_session(ex=None):
    reset_session()

@app.route('/')
def index():
    return render_template('index.html', website_info=configuration_handler.load('website'))

@app.route('/join', methods=['POST'])
@validate_user_identifier
def join_game():
    if sufficent_funds(request.cookies.get('identifier'), float(request.form['bet-amount'])):
        init_game(request.cookies.get('identifier'), float(request.form['bet-amount']))
        return render_template('blackjack.html', website_info=configuration_handler.load('website'))

    return 'insufficent funds'

@socketio.on('client_connected')
@validate_client
def client_connect(data):
    deck_handler.draw(data['identifier'], Status.visible)
    deck_handler.draw(data['identifier'], Status.hidden)

    deck_handler.draw(get_cpu_identifier(data['identifier']), Status.visible)
    deck_handler.draw(get_cpu_identifier(data['identifier']), Status.hidden)
    
    socketio.emit('update_table', json.dumps(update_table(data['identifier'])))

    if isGameOver(data['identifier']):
        client_stand(data)

@socketio.on('client_hit')
@validate_client
def client_hit(data):
    deck_handler.draw(data['identifier'], Status.visible)

    socketio.emit('update_table', json.dumps(update_table(data['identifier'])))

    if isGameOver(data['identifier']):
        client_stand(data)

@socketio.on('client_stand')
@validate_client
def client_stand(data):
    simulate_cpu(data['identifier'], socketio)
    payout_bet(data['identifier'])
    socketio.emit('game_finished', json.dumps(finish_game(data['identifier'])))

@socketio.on('client_doubledown')
@validate_client
def client_doubledown(data):
    if doubledown_valid(data['identifier']):
        if sufficent_funds(data['identifier'], current_bet(data['identifier'])):
            deck_handler.draw(data['identifier'], Status.hidden)
            double_bet(data['identifier'])
            socketio.emit('update_table', json.dumps(update_table(data['identifier'])))
            client_stand(data)
        else:
            socketio.emit('error', {'message': 'insufficent funds'})
    

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0' , port=5000)