from init_app import db

from models import Active_card, Card, Status, Game

import os, random

def init_deck(game_id):
    for card in db.session.query(Card).all():
        db.session.add(Active_card(card.id, game_id))
        
    db.session.commit()

def draw(identifier, status):    
    if db.session.query(Game).filter(Game.player == identifier).count():
        deck = db.session.query(Active_card).filter(Active_card.game_identifier == db.session.query(Game).filter(Game.player == identifier).one().id).filter(Active_card.owner == None).all()
    else:
        deck = db.session.query(Active_card).filter(Active_card.game_identifier == db.session.query(Game).filter(Game.cpu_hand_identifier == identifier).one().id).filter(Active_card.owner == None).all()

    card = deck[random.randint(0, len(deck)) - 1]

    print('Card drawn with id ' + str(card.id))

    card.owner = identifier
    card.status = status

    db.session.commit()