from models import Game, Active_card, Game_state, User, Status, Card
from init_app import db, socketio

from flask import redirect
from functools import wraps 

from general_handlers.deck_handler import draw
from general_handlers.game_handler import doubledown_valid, calculate_hand
from general_handlers.user_handler import remove_user_from_active_games
from general_handlers.balance_handler import remove_balance

import random, string, json

def init_game(player, bet):

    remove_user_from_active_games(player)

    cpu_hand_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(45))

    remove_balance(player, bet)

    print('Removed bet amount from user')

    db.session.add(Game(player, bet, cpu_hand_identifier))
    db.session.commit()
    print('Init game + commited to database')

    return db.session.query(Game).filter(Game.player == player).one().id

def isIngame(identifier):
    print('Validating identifier ' + identifier)

    if db.session.query(Game).filter(Game.player == identifier).count():
        return True
    else:
        return False

def get_cpu_identifier(identifier):
    return db.session.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier

def update_table(identifier):    
    game = db.session.query(Game).filter(Game.player == identifier).one()

    player_hand = db.session.query(Active_card).filter(Active_card.owner == identifier).all()
    cpu_hand = db.session.query(Active_card).filter(Active_card.owner == game.cpu_hand_identifier).all()

    print('Got hands')

    table_data = {
        'player_cards': [],
        'cpu_cards': [],
        'doubledown': doubledown_valid(identifier),
        'bet': db.session.query(Game).filter(Game.player == identifier).one().bet 
    }
    print('Got doubledown and bet status')

    for card in player_hand:
        card_data = {
            'image': db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        table_data['player_cards'].append(card_data)
    
    print('Got player images')
    
    for card in cpu_hand:

        if card.status == Status.visible:
            image_name = db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        else:
            image_name = 'red_back'

        card_data = {
            'image': image_name
        }
        table_data['cpu_cards'].append(card_data)
    
    print('Got cpu images')

    print(table_data)

    return table_data

def get_game_state(identifier):
    game = db.session.query(Game).filter(Game.player == identifier).one()

    player_value = calculate_hand(identifier)
    cpu_value = calculate_hand(game.cpu_hand_identifier)

    player_cards = db.session.query(Active_card).filter(Active_card.owner == identifier).count()
    cpu_cards = db.session.query(Active_card).filter(Active_card.owner == game.cpu_hand_identifier).count()

    print('Player hand ' + str(player_value))
    print('Cpu hand ' + str(cpu_value))

    if player_value > 21:
        current_gamestate = Game_state.player_busted
    elif cpu_value > 21:
        current_gamestate = Game_state.cpu_busted

    elif cpu_value == 21 and cpu_cards == 2:
        current_gamestate = Game_state.cpu_blackjack
    elif player_value == 21 and player_cards == 2:
        current_gamestate = Game_state.player_blackjack

    elif player_value > cpu_value:
        current_gamestate = Game_state.player_lead
    elif player_value < cpu_value:
        current_gamestate = Game_state.cpu_lead

    elif player_value == cpu_value:
        current_gamestate = Game_state.draw
    
    return current_gamestate

def simulate_cpu(identifier, sid):
    cpu_identifer = db.session.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier

    while True:
        if get_game_state(identifier) == Game_state.player_busted or calculate_hand(cpu_identifer) > 16:
            break
        else:
            draw(cpu_identifer, Status.visible)
            socketio.emit('update_table', json.dumps(update_table(identifier)), room=sid)

def finish_game(identifier):
    game_data = {
        'player_cards': [],
        'cpu_cards': []
    }

    for card in db.session.query(Active_card).filter(Active_card.owner == identifier).all():
        card_data = {
            'image': db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        game_data['player_cards'].append(card_data)

    for card in db.session.query(Active_card).filter(Active_card.owner == db.session.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier).all():
        card_data = {
            'image': db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        game_data['cpu_cards'].append(card_data)
    
    game_state = get_game_state(identifier)

    if game_state == Game_state.player_busted:
        game_data['result'] = 'You busted'
    elif game_state == Game_state.cpu_busted:
        game_data['result'] = 'Cpu busted'
    elif game_state == Game_state.cpu_blackjack:
        game_data['result'] = 'Cpu got blackjack'
    elif game_state == Game_state.player_blackjack:
        game_data['result'] = 'You got blackjack'
    elif game_state == Game_state.cpu_lead:
        game_data['result'] = 'Cpu won by points'
    elif game_state == Game_state.player_lead:
        game_data['result'] = 'You won by points'
    elif game_state == Game_state.draw:
        game_data['result'] = 'Draw'
    
    delete_game(db.session.query(Game).filter(Game.player == identifier).one().id)

    return game_data

def isGameOver(identifier):
    game_state = get_game_state(identifier)

    if game_state == Game_state.cpu_blackjack or game_state == Game_state.player_blackjack or game_state == Game_state.player_busted:
        return True
    return False

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