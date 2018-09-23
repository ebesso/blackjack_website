from models import Game, User, Game_state
from init_app import db

from general_handlers import configuration_handler
import os
            
def sufficent_funds(identifier, amount):
    if amount > db.session.query(User).filter(User.identifier == identifier).one().balance:
        return False
    return True

def add_balance(identifier, amount):
    user = db.session.query(User).filter(User.identifier == identifier).one()

    user.balance += amount
    db.session.commit

def remove_balance(identifier, amount):
    user = db.session.query(User).filter(User.identifier == identifier).one()

    user.balance -= amount
    db.session.commit





    



