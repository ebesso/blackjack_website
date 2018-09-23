from flask import render_template, request, redirect

from init_app import db

from models import User

from multiplayer.handlers import table_handler
from general_handlers.user_handler import validate_user_identifier, identifier_to_steamid

from general_handlers import configuration_handler

from . import multiplayer

@multiplayer.route('/multi')
def multi_index():
    return render_template('multiplayer/index.html', website_info=configuration_handler.load('website'))

@multiplayer.route('/multi/join', methods=['POST'])
@validate_user_identifier
def join_multi():
    if 'room_key' in request.form and request.form['room_key'] != '':
        if table_handler.table_exist(request.form['room_key']):
            print('valid room key')
            if table_handler.isFull(table_handler.identifier_to_id(request.form['room_key'])):
                print('room is full')
            else:
                table_handler.join_table(table_handler.identifier_to_id(request.form['room_key']), identifier_to_steamid(request.cookies.get('identifier')))
                print('Joined room')
                return render_template('multiplayer/blackjack.html', website_info=configuration_handler.load('website'))

        else:   
            print('Invalid room key')

    else:
        print('Auto joining room')
        table_handler.auto_join(identifier_to_steamid(request.cookies.get('identifier')))

        print('Joined room')
        return render_template('multiplayer/blackjack.html', website_info=configuration_handler.load('website'))
    
    return redirect('/multi')