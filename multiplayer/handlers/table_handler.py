from init_app import db, socketio

from functools import wraps
from flask import redirect

from general_handlers import configuration_handler
from general_handlers.user_handler import identifier_to_steamid, steamid_to_identifer, remove_user_from_active_games
from general_handlers import balance_handler
from general_handlers.deck_handler import init_deck

from models import User, Table, Active_player, Player_status

import random, string, enum, json

class options(enum.Enum):
    play = 1
    bet = 2

def table_exist(identifier):
    if db.session.query(Table).filter(Table.identifier == identifier).count():
        return True
    return False

def isFull(table_id):
    if db.session.query(Active_player).filter(Active_player.table_id == table_id).count() < int(configuration_handler.load('table').max_players) + 1:
        return False
    return True

def identifier_to_id(identifier):
    return db.session.query(Table).filter(Table.identifier == identifier).one().id

def join_table(table_id, steamid):
    remove_user_from_active_games(steamid)

    player = Active_player(steamid, table_id)
    
    db.session.add(player)
    db.session.commit()

def leave_table(steamid):
    db.session.query(Active_player).filter(Active_player.steamid == steamid).delete()
    db.session.commit()

def auto_join(steamid):
    if db.session.query(Table).count():
        for table in db.session.query(Table).all():
            if isFull(table.id) == False:
                join_table(table.id, steamid)
                print('Joined current room')
                return
    
    print('Had to create new room')
    
    create_table()
    auto_join(steamid)

def create_table():
    deck_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))
    init_deck(deck_identifier)

    db.session.add(Table(deck_identifier))
    db.session.commit()

def isIngame(identifier):
    if db.session.query(Active_player).filter(Active_player.steamid == identifier_to_steamid(identifier)).count():
       return True 

    return False

def get_current_table(steamid):
    return db.session.query(Table).filter(Table.id == db.session.query(Active_player).filter(Active_player.steamid == steamid).one().table_id).one()

def get_turn(table_id):
    return db.session.query(Table).filter(Table.id == table_id).one().player_turn

def validate_bet(identifier, amount):
    steamid = identifier_to_steamid(identifier)

    if get_turn(db.session.query(Active_player).filter(Active_player.steamid == steamid).one().table_id) == None:
        if balance_handler.sufficent_funds(identifier, amount):
            if db.session.query(Active_player).filter(Active_player.steamid == steamid).one().bet == None:
                balance_handler.remove_balance(identifier, amount)
                
                player = db.session.query(Active_player).filter(Active_player.steamid == steamid).one()
                player.bet = amount
                player.status_string = 'Betted ' + str(amount) + '$'
                player.has_played = True
                player.status = Player_status.active

                db.session.commit()

                return 'Bet placed'
            return 'You have already placed bet'
        return 'Insufficent funds'
    return 'Bets not allowed atm'

def send_options(steamid, option):
    sid = db.session.query(Active_player).filter(Active_player.steamid == steamid).one().session_id

    if option == options.bet:
        option_data = {
            'message': 'Please bet',
            'action_required': 'bet'
        }

    elif option == options.play:
        option_data = {
            'message': 'Make a play',
            'action_required': 'play'
        }

    socketio.emit('client_action_required', json.dumps(option_data), room=sid)

def validate_client(func):
    @wraps(func)
    def validate(data):
        print('Validating client')        
        if 'identifier' in data:
            if isIngame(data['identifier']):
                return func(data)
            else:
                return redirect('/')
        else:
            return redirect('/login')
        
    return validate

        
            

