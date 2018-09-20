from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Game, User, Game_state

from game_handler import get_game_state

import configuration_handler

import os

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def sufficent_funds(identifier, amount):
    db = Session()

    if amount > db.query(User).filter(User.identifier == identifier).one().balance:
        return False
    return True

def double_bet(identifier):
    db = Session()
    game = db.query(Game).filter(Game.player == identifier).one()

    user = db.query(User).filter(User.identifier == identifier).one()
    user -= game.bet
    db.commit()

    game.bet = game.bet * 2

    db.commit()

def payout_bet(identifier):
    db = Session()

    game = db.query(Game).filter(Game.player == identifier).one()

    payout_config = configuration_handler.load('payouts')

    game_state = get_game_state(identifier)
    print('Got game state')

    if game_state == Game_state.player_blackjack:
        user = db.query(User).filter(User.identifier == identifier).one()
        user.balance += game.bet * float(payout_config.blackjack)
        db.commit()

        print('Payed out ' + str(game.bet * float(payout_config.blackjack)))

    elif game_state == Game_state.player_lead:
        user = db.query(User).filter(User.identifier == identifier).one()
        user.balacne += game.bet * float(payout_config.regular)
        db.commit()

        print('Payed out ' + str(game.bet * float(payout_config.regular)))
    
def current_bet(identifier):
    db = Session()

    return db.query(Game).filter(Game.player == identifier).one().bet




    



