from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Game, Active_card, Card, Status, Ranks, Game_state
from deck_handler import init_deck, draw

import os, random, string, json

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def init_game(player, bet):
    db = Session()

    if db.query(Game).filter(Game.player == player).count():
        delete_game(db.query(Game).filter(Game.player == player).one().id)

    cpu_hand_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(45))

    db.add(Game(player, bet, cpu_hand_identifier))
    db.commit()

    gameid = db.query(Game).filter(Game.player == player).one().id

    init_deck(gameid)

def delete_game(gameid):
    db = Session()

    db.query(Game).filter(Game.id == gameid).delete()
    db.query(Active_card).filter(Active_card.game_identifier == gameid).delete()

    db.commit()

def isIngame(identifier):
    db = Session()

    print('Validating identifier ' + identifier)

    if db.query(Game).filter(Game.player == identifier).count():
        return True
    else:
        return False

def get_cpu_identifier(identifier):
    return Session().query(Game).filter(Game.player == identifier).one().cpu_hand_identifier

def update_table(identifier):
    db = Session()
    
    game = db.query(Game).filter(Game.player == identifier).one()

    player_hand = db.query(Active_card).filter(Active_card.owner == identifier).all()
    cpu_hand = db.query(Active_card).filter(Active_card.owner == game.cpu_hand_identifier).all()

    table_data = {
        'player_cards': [],
        'cpu_cards': []
    }

    for card in player_hand:
        card_data = {
            'image': db.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        table_data['player_cards'].append(card_data)
    
    for card in cpu_hand:

        if card.status == Status.visible:
            image_name = db.query(Card).filter(Card.id == card.card_identifier).one().image_name
        else:
            image_name = 'red_back'

        card_data = {
            'image': image_name
        }
        table_data['cpu_cards'].append(card_data)
    
    print(table_data)

    return table_data

def calculate_hand(identifier):
    db = Session()

    hand = db.query(Active_card).filter(Active_card.owner == identifier).all()

    hand_value = 0
    ace_hand_value = 0

    for card in hand:
        hand_value += db.query(Card).filter(Card.id == card.card_identifier).one().blackjack_value
    
    for card in hand:
        if db.query(Card).filter(Card.id == card.card_identifier).one().rank == Ranks.ace:
            ace_hand_value = hand_value - 10
    
    if hand_value > 21 and ace_hand_value != 0:
        return ace_hand_value
    
    else:
        return hand_value
    
def get_game_state(identifier):
    db = Session()

    game = db.query(Game).filter(Game.player == identifier).one()

    player_value = calculate_hand(identifier)
    cpu_value = calculate_hand(game.cpu_hand_identifier)

    print('Player hand ' + str(player_value))
    print('Cpu hand ' + str(cpu_value))
    

    if player_value > 21:
        return Game_state.player_busted
    elif cpu_value > 21:
        return Game_state.cpu_busted

    elif cpu_value == 21 and db.query(Active_card).filter(Active_card.owner == game.cpu_hand_identifier).count() == 2:
        return Game_state.cpu_blackjack
    elif player_value == 21 and db.query(Active_card).filter(Active_card.owner == identifier).count() == 2:
        return Game_state.player_blackjack

    elif player_value > cpu_value:
        return Game_state.player_lead
    elif player_value < cpu_value:
        return Game_state.cpu_lead

    elif player_value == cpu_value:
        return Game_state.draw

def simulate_cpu(identifier, socketio):
    db = Session()

    cpu_identifer = db.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier

    while True:
        if calculate_hand(cpu_identifer) > 16 or get_game_state == Game_state.player_busted:
            break
        else:
            draw(cpu_identifer, Status.visible)
            socketio.emit('update_table', json.dumps(update_table(identifier)))

def finish_game(identifier):
    db = Session()

    game_data = {
        'player_cards': [],
        'cpu_cards': []
    }

    for card in db.query(Active_card).filter(Active_card.owner == identifier).all():
        card_data = {
            'image': db.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        game_data['player_cards'].append(card_data)

    for card in db.query(Active_card).filter(Active_card.owner == db.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier).all():
        card_data = {
            'image': db.query(Card).filter(Card.id == card.card_identifier).one().image_name
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
    
    delete_game(db.query(Game).filter(Game.player == identifier).one().id)

    return game_data
            
