from flask import request

from init_app import socketio, db

from models import Status, Game

from general_handlers.deck_handler import draw
from general_handlers.game_handler import doubledown_valid
from general_handlers.balance_handler import sufficent_funds
from general_handlers.user_handler import identifier_to_steamid

from singleplayer.handlers.game_handler import get_cpu_identifier, isGameOver, validate_client, update_table, simulate_cpu, finish_game
from singleplayer.handlers.balance_handler import payout_bet, double_bet, current_bet

import json

@socketio.on('single_client_connected')
@validate_client
def client_connect(data):
    print('Client has connected')

    deck_identifier = db.session.query(Game).filter(Game.player_steamid == identifier_to_steamid(data['identifier'])).one().deck_identifier

    draw(identifier_to_steamid(data['identifier']), deck_identifier,Status.visible)
    draw(identifier_to_steamid(data['identifier']), deck_identifier,Status.hidden)

    draw(get_cpu_identifier(data['identifier']), deck_identifier, Status.visible)
    draw(get_cpu_identifier(data['identifier']), deck_identifier, Status.hidden)
    
    socketio.emit('update_table', json.dumps(update_table(data['identifier'])), room=request.sid)

    if isGameOver(identifier_to_steamid(data['identifier'])):
        client_stand(data)

@socketio.on('single_client_hit')
@validate_client
def client_hit(data):
    draw(identifier_to_steamid(data['identifier']), db.session.query(Game).filter(Game.player_steamid == identifier_to_steamid(data['identifier'])).one().deck_identifier, Status.visible)

    socketio.emit('update_table', json.dumps(update_table(data['identifier'])), room=request.sid)

    if isGameOver(identifier_to_steamid(data['identifier'])):
        client_stand(data)

@socketio.on('single_client_stand')
@validate_client
def client_stand(data):
    simulate_cpu(identifier_to_steamid(data['identifier']), request.sid)
    payout_bet(identifier_to_steamid(data['identifier']))
    
    socketio.emit('game_finished', json.dumps(finish_game(data['identifier'])), room=request.sid)

@socketio.on('single_client_doubledown')
@validate_client
def client_doubledown(data):
    if doubledown_valid(data['identifier']):
        if sufficent_funds(data['identifier'], current_bet(data['identifier'])):
            draw(identifier_to_steamid(data['identifier']), db.session.query(Game).filter(Game.player_steamid == identifier_to_steamid(data['identifier'])).one().deck_identifier, Status.hidden)
            double_bet(data['identifier'])
            
            socketio.emit('update_table', json.dumps(update_table(data['identifier'])), room=request.sid)

            client_stand(data)
        else:
            socketio.emit('error', {'message': 'insufficent funds'}, room=request.sid)