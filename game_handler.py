from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Game
from deck_handler import init_deck

import os, random, string

db_engine = create_engine(os.environ['blackjack_database_url'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def init_game(player, bet):
    db = Session()

    player_hand_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(45))
    cpu_hand_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(45))

    db.add(Game(player, bet, player_hand_identifier, cpu_hand_identifier))
    db.commit()

    gameid = db.query(Game).filter(Game.player_hand_identifier == player_hand_identifier).one().id

    init_deck(gameid)
        