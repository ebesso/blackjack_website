from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Game, Active_card, Card, Status
from deck_handler import init_deck

import os, random, string

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def init_game(player, bet):
    db = Session()

    if db.query(Game).filter(Game.player == player).filter(Game.active == True).count():
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

def isIngame(identifier):
    db = Session()

    print('Validating identifier ' + identifier)

    if db.query(Game).filter(Game.player == identifier).filter(Game.active == True).count():
        return True
    else:
        return False

def get_cpu_identifier(identifier):
    return Session().query(Game).filter(Game.player == identifier).filter(Game.active == True).one().cpu_hand_identifier

def update_table(identifier):
    db = Session()
    
    game = db.query(Game).filter(Game.player == identifier).filter(Game.active == True).one()

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

    if db.query(Game).filter(Game.player == identifier).filter(Game.active == True).count():
        gameid = db.query(Game).filter(Game.player == identifier).filter(Game.active == True).one().id
    else:
        gameid = db.query(Game).filter(Game.cpu_hand_identifier == identifier).filter(Game.active == True).one().id

    