from models import Game, User, Game_state
from init_app import db

from general_handlers import configuration_handler
from singleplayer.handlers.game_handler import get_game_state
import os
            
def sufficent_funds(identifier, amount):
    if amount > db.session.query(User).filter(User.identifier == identifier).one().balance:
        return False
    return True

def double_bet(identifier):
    game = db.session.query(Game).filter(Game.player == identifier).one()

    user = db.session.query(User).filter(User.identifier == identifier).one()
    user.balance -= game.bet
    db.session.commit()

    game.bet = game.bet * 2

    db.session.commit()

def payout_bet(identifier):
    game = db.session.query(Game).filter(Game.player == identifier).one()

    payout_config = configuration_handler.load('payouts')

    game_state = get_game_state(identifier)
    print('Got game state')

    if game_state == Game_state.player_blackjack:
        user = db.session.query(User).filter(User.identifier == identifier).one()
        user.balance += game.bet * float(payout_config.blackjack)
        db.session.commit()

        print('Payed out ' + str(game.bet * float(payout_config.blackjack)))

    elif game_state == Game_state.player_lead or game_state == Game_state.cpu_busted:
        user = db.session.query(User).filter(User.identifier == identifier).one()
        user.balance += game.bet * float(payout_config.regular)
        db.session.commit()

        print('Payed out ' + str(game.bet * float(payout_config.regular)))

def current_bet(identifier):
    return db.session.query(Game).filter(Game.player == identifier).one().bet




    



