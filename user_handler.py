from flask import request, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from functools import wraps

from models import User

import os, random, string

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def authorize_user(steamid):
    db = Session()

    if db.query(User).filter(User.steamid == steamid).count():
        user = db.query(User).filter(User.steamid == steamid).one()

        identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        user.identifier = identifier

        db.commit()

        return identifier
    
    else:
        print('New user')

        identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

        user = User(steamid, 100, identifier)

        db.add(user)
        db.commit()

        return identifier

def valid_user_identifier(identifier):
    db = Session()

    if db.query(User).filter(User.identifier == identifier).count():
        return True
    else:
        return False


def validate_user_identifier(func):
    @wraps(func)
    def validate():
        print('Identifier exists')

        if 'identifier' in request.cookies:
            if validate_user_identifier:
                return func()
        else:
            return redirect('/login')
    return validate

    