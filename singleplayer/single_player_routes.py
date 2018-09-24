from flask import Blueprint, render_template, request

from general_handlers import user_handler, configuration_handler, balance_handler, deck_handler
from singleplayer.handlers import game_handler

from . import singleplayer

@singleplayer.route('/single')
def single_index():
    return render_template('singleplayer/index.html', website_info=configuration_handler.load('website'))

@singleplayer.route('/single/join', methods=['POST'])
@user_handler.validate_user_identifier
def join_game():
    if balance_handler.sufficent_funds(request.cookies.get('identifier'), float(request.form['bet-amount'])):
        deck_identifier = game_handler.init_game(request.cookies.get('identifier'), float(request.form['bet-amount']))
        deck_handler.init_deck(deck_identifier)

        return render_template('singleplayer/blackjack.html', website_info=configuration_handler.load('website'))

    return 'insufficent funds'  