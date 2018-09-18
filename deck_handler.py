from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Active_card, Card, Status, Game

import os, random

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def init_deck(game_id):
    db = Session()

    for card in db.query(Card).all():
        db.add(Active_card(card.id, game_id))
        
    db.commit()

def draw(identifier, status):
    db = Session()
    
    if db.query(Game).filter(Game.player == identifier).count():
        deck = db.query(Active_card).filter(Active_card.game_identifier == db.query(Game).filter(Game.player == identifier).one().id).filter(Active_card.owner == None).all()
    else:
        deck = db.query(Active_card).filter(Active_card.game_identifier == db.query(Game).filter(Game.cpu_hand_identifier == identifier).one().id).filter(Active_card.owner == None).all()

    card = deck[random.randint(0, len(deck)) - 1]

    print(card.id)

    card.owner = identifier
    card.status = status

    db.commit()


