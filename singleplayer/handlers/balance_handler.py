from init_app import db

from models import Game, User, Game_state

from general_handlers import configuration_handler
from general_handlers.balance_handler import add_balance, remove_balance
from general_handlers.user_handler import steamid_to_identifer, identifier_to_steamid

from singleplayer.handlers.game_handler import get_game_state

def double_bet(identifier):
    game = db.session.query(Game).filter(Game.player_steamid == identifier_to_steamid(identifier)).one()

    remove_balance(identifier, game.bet)

    game.bet = game.bet * 2
    db.session.commit()

def payout_bet(steamid):
    game = db.session.query(Game).filter(Game.player_steamid == steamid).one()

    payout_config = configuration_handler.load('payouts')

    game_state = get_game_state(steamid)
    print('Got game state')

    if game_state == Game_state.player_blackjack:
        add_balance(steamid_to_identifer(steamid), game.bet * float(payout_config.blackjack))

        print('Payed out ' + str(game.bet * float(payout_config.blackjack)))

    elif game_state == Game_state.player_lead or game_state == Game_state.cpu_busted:
        add_balance(steamid_to_identifer(steamid), game.bet * float(payout_config.regular))

        print('Payed out ' + str(game.bet * float(payout_config.regular)))

def current_bet(identifier):
    return db.session.query(Game).filter(Game.player == identifier).one().bet