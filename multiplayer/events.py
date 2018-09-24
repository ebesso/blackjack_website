from init_app import socketio, db

from flask import request

from models import Active_player, Status

from multiplayer.handlers import table_handler, round_handler

from general_handlers.user_handler import identifier_to_steamid
from general_handlers.deck_handler import draw

import json

@socketio.on('multi_client_connect')
@table_handler.validate_client
def client_connect(data):
    print('Client has connected to table')

    player = db.session.query(Active_player).filter(Active_player.steamid == identifier_to_steamid(data['identifier'])).filter(Active_player.session_id == None).one()
    player.session_id = request.sid

    db.session.commit()

    if table_handler.get_turn(table_handler.get_current_table(identifier_to_steamid(data['identifier'])).id) != None:
        socketio.emit('client_message', {'message': 'Wait till next round'}, room=request.sid)

    round_handler.round_action(data['identifier'])
    

@socketio.on('multi_client_action')
def client_action(data):
    if data['action'] == 'bet':
        response = table_handler.validate_bet(data['identifier'], data['amount'])
        socketio.emit('client_message', {'message': response}, room=request.sid)

    elif data['action'] == 'hit':
        draw(identifier_to_steamid(data['identifier']), table_handler.get_current_table(identifier_to_steamid(data['identifier'])).deck_identifier, Status.visible)
    
    round_handler.round_action(data['identifier'])