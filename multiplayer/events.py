from init_app import socketio, db

from flask import request

from models import Active_player

from multiplayer.handlers import table_handler
from general_handlers.user_handler import identifier_to_steamid

import json

@socketio.on('multi_client_connect')
@table_handler.validate_client
def client_connect(data):
    print('Client has connected to table')

    player = db.session.query(Active_player).filter(Active_player.steamid == identifier_to_steamid(data['identifier'])).filter(Active_player.session_id == None).one()
    player.session_id = request.sid

    db.session.commit()

    if table_handler.isTable_empty(table_handler.get_current_table(identifier_to_steamid(data['identifier'])).id):
        socketio.emit('client_message', json.dumps({'message': 'Wait for more players to join'}), room=request.sid)

    elif table_handler.get_turn(table_handler.get_current_table(data['identifier'])) != None:
        socketio.emit('client_message', {'message': 'Wait till next round'}, room=request.sid)
    
    else:
        socketio.emit('client_message', {'message': 'New round has just started'}, room=request.sid)

@socketio.on('multi_client_action')
def client_action(data):
    if data['action'] == 'bet':
        response = table_handler.validate_bet(data['identifier'], data['amount'])
        socketio.emit('client_message', {'message': response}, room=request.sid)
