from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Active_card, Card, Status

import os

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def init_deck(game_id):
    db = Session()

    for card in db.query(Card).all():
        db.add(Active_card(card.id, game_id))
        
    db.commit()