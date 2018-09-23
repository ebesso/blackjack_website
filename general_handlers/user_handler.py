from flask import request, redirect

from functools import wraps
import os, random, string

from models import User, Active_player, Game, Active_card

from init_app import db


def valid_user_identifier(identifier):
    print('Validating user identifier')

    if db.session.query(User).filter(User.identifier == identifier).count():
        return True
    else:
        return False

def authorize_user(steamid):
    if db.session.query(User).filter(User.steamid == steamid).count():
        user = db.session.query(User).filter(User.steamid == steamid).one()

        identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        user.identifier = identifier

        db.session.commit()

        return identifier
    
    else:
        print('New user')

        identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

        user = User(steamid, 100, identifier)

        db.session.add(user)
        db.session.commit()

        return identifier

def validate_user_identifier(func):
    @wraps(func)
    def validate():
        if 'identifier' in request.cookies:
            print('identifier exists')
            if valid_user_identifier(request.cookies.get('identifier')):
                print('identifier is valid')
                return func()
            else:
                print('identifier is invalid')
                return redirect('/login')
        else:
            print('identifier does not exist')
            return redirect('/login')
    return validate

def identifier_to_steamid(identifier):
    return db.session.query(User).filter(User.identifier == identifier).one().steamid

def steamid_to_identifer(steamid):
    return db.session.query(User).filter(User.steamid == steamid).one().identifier


def remove_user_from_active_games(identifier):
    if db.session.query(Game).filter(Game.player == identifier).count():
        gameid = db.session.query(Game).filter(Game.player == identifier).one().id

        db.session.query(Active_card).filter(Active_card.game_identifier == gameid).delete()
        db.session.query(Game).filter(Game.id == gameid).delete()

        db.session.commit()
    
    if db.session.query(Active_player).filter(Active_player.steamid == identifier_to_steamid(identifier)).count():
        db.session.query(Active_player).filter(Active_player.steamid == identifier_to_steamid(identifier)).delete()

        db.session.commit()

        