from init_app import db

from models import Active_card, Card, Status, Game
from general_handlers.user_handler import identifier_to_steamid

import os, random

def init_deck(deck_identifier):
    for card in db.session.query(Card).all():
        db.session.add(Active_card(card.id, deck_identifier))
        
    db.session.commit()

def draw(identifier, deck_identifier, status):

    deck = db.session.query(Active_card).filter(Active_card.deck_identifier == deck_identifier).filter(Active_card.owner == None).all()

    card = deck[random.randint(0, len(deck)) - 1]

    print('Card drawn with id ' + str(card.id))

    card.owner = identifier
    card.status = status

    db.session.commit()