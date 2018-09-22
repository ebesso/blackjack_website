from flask import request
from init_app import socketio, db

from models import User

import json

@socketio.on('client_balance')
def client_balance(data):
    print('Client requested balance update')
    socketio.emit('balance_update', json.dumps({'balance': db.session.query(User).filter(User.identifier == data['identifier']).one().balance}), room=request.sid)