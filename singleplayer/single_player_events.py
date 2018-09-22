from flask import request

from init_app import socketio

from models import Status

from general_handlers.deck_handler import draw
from general_handlers.game_handler import doubledown_valid
from singleplayer.handlers.game_handler import get_cpu_identifier, isGameOver, validate_client, update_table, simulate_cpu, finish_game
from general_handlers.balance_handler import payout_bet, sufficent_funds, current_bet, double_bet

import json

@socketio.on('client_connected')
@validate_client
def client_connect(data):
    print('Client has connected')

    draw(data['identifier'], Status.visible)
    draw(data['identifier'], Status.hidden)

    draw(get_cpu_identifier(data['identifier']), Status.visible)
    draw(get_cpu_identifier(data['identifier']), Status.hidden)
    
    socketio.emit('update_table', json.dumps(update_table(data['identifier'])), room=request.sid)

    if isGameOver(data['identifier']):
        client_stand(data)

@socketio.on('client_hit')
@validate_client
def client_hit(data):
    draw(data['identifier'], Status.visible)

    socketio.emit('update_table', json.dumps(update_table(data['identifier'])), room=request.sid)

    if isGameOver(data['identifier']):
        client_stand(data)

@socketio.on('client_stand')
@validate_client
def client_stand(data):
    simulate_cpu(data['identifier'], request.sid)
    payout_bet(data['identifier'])
    
    socketio.emit('game_finished', json.dumps(finish_game(data['identifier'])), room=request.sid)

@socketio.on('client_doubledown')
@validate_client
def client_doubledown(data):
    if doubledown_valid(data['identifier']):
        if sufficent_funds(data['identifier'], current_bet(data['identifier'])):
            draw(data['identifier'], Status.hidden)
            double_bet(data['identifier'])
            
            socketio.emit('update_table', json.dumps(update_table(data['identifier'])), room=request.sid)

            client_stand(data)
        else:
            socketio.emit('erraor', {'message': 'insufficent funds'}, room=request.sid)