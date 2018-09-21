from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc as sa_exc

from initializer import init_cards, init_database

from user_handler import valid_user_identifier, isIngame
from game_handler import init_game, update_table, get_cpu_identifier, update_table, isGameOver, finish_game, simulate_cpu, doubledown_valid
from balance_handler import double_bet, sufficent_funds, current_bet, payout_bet

import deck_handler

import configuration_handler

from models import Status, Game_state, User

from user_login import user_login_bp

from functools import wraps
import json, os, warnings

app = Flask(__name__)

app.secret_key = '123'
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)
socketio = SocketIO(app)

init_database()
init_cards()

app.register_blueprint(user_login_bp)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)

def validate_user_identifier(func):
    @wraps(func)
    def validate():
        if 'identifier' in request.cookies:
            print('identifier exists')
            if valid_user_identifier(request.cookies.get('identifier'), db):
                print('identifier is valid')
                return func()
            else:
                print('identifier is invalid')
                return redirect('/login')
        else:
            print('identifier does not exist')
            return redirect('/login')
    return validate

def validate_client(func):
    @wraps(func)
    def validate(data):
        if 'identifier' in data:
            if isIngame(data['identifier'], db):
                return func(data)
            else:
                return redirect('/')
        else:
            return redirect('/login')
        
    return validate

@app.route('/')
def index():
    
    if valid_user_identifier(request.cookies.get('identifier'), db):
        balance_string = 'Balance: ' + str(db.session.query(User).filter(User.identifier == request.cookies.get('identifier')).one().balance) + '$'
    else:
        balance_string = ''

    return render_template('index.html', website_info=configuration_handler.load('website'), balance=balance_string)

@app.route('/join', methods=['POST'])
@validate_user_identifier
def join_game():
    if sufficent_funds(request.cookies.get('identifier'), float(request.form['bet-amount']), db):
        gameid = init_game(request.cookies.get('identifier'), float(request.form['bet-amount']), db)
        deck_handler.init_deck(gameid, db)

        return render_template('blackjack.html', website_info=configuration_handler.load('website'))

    return 'insufficent funds'

@socketio.on('client_connected')
@validate_client
def client_connect(data):
    deck_handler.draw(data['identifier'], Status.visible, db)
    deck_handler.draw(data['identifier'], Status.hidden, db)

    deck_handler.draw(get_cpu_identifier(data['identifier'], db), Status.visible, db)
    deck_handler.draw(get_cpu_identifier(data['identifier'], db), Status.hidden, db)
    
    socketio.emit('update_table', json.dumps(update_table(data['identifier'], db)), room=request.sid)

    if isGameOver(data['identifier'], db):
        client_stand(data)

@socketio.on('client_hit')
@validate_client
def client_hit(data):
    deck_handler.draw(data['identifier'], Status.visible, db)

    socketio.emit('update_table', json.dumps(update_table(data['identifier'], db)), room=request.sid)

    if isGameOver(data['identifier'], db):
        client_stand(data)

@socketio.on('client_stand')
@validate_client
def client_stand(data):
    simulate_cpu(data['identifier'], socketio, db, request.sid)
    payout_bet(data['identifier'], db)
    socketio.emit('game_finished', json.dumps(finish_game(data['identifier'], db)), room=request.sid)

@socketio.on('client_doubledown')
@validate_client
def client_doubledown(data):
    if doubledown_valid(data['identifier'], db):
        if sufficent_funds(data['identifier'], current_bet(data['identifier'], db), db):
            deck_handler.draw(data['identifier'], Status.hidden, db)
            double_bet(data['identifier'], db)
            socketio.emit('update_table', json.dumps(update_table(data['identifier'], db)), room=request.sid)
            client_stand(data)
        else:
            socketio.emit('erraor', {'message': 'insufficent funds'}, room=request.sid)

@socketio.on('client_balance')
def client_balance(data):
    print('Client requested balance update')
    socketio.emit('balance_update', json.dumps({'balance': db.session.query(User).filter(User.identifier == data['identifier']).one().balance}), room=request.sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))        
    socketio.run(app, host='0.0.0.0' , port=port)