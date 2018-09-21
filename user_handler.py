from flask import request, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from functools import wraps

from models import User

from game_handler import isIngame

import os, random, string

def authorize_user(steamid, db):
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

def valid_user_identifier(identifier, db):
    print('Validating user identifier')

    if db.session.query(User).filter(User.identifier == identifier).count():
        return True
    else:
        return False

    