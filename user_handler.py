from flask import request, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from functools import wraps

from models import User

from game_handler import isIngame

import os, random, string

db_engine = create_engine(os.environ['DATABASE_URL'])
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

    print('Validating identifier: ' + identifier)

    if db.query(User).filter(User.identifier == identifier).count():
        return True
    else:
        return False


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

def validate_client(func):
    @wraps(func)
    def validate(data):
        if 'identifier' in data:
            if isIngame(data['identifier']):
                return func(data)
            else:
                return redirect('/')
        else:
            return redirect('/login')
        
    return validate

    