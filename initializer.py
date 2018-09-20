from models import Card, Ranks, Colors, Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import os

db_engine = create_engine(os.environ['DATABASE_URL'])
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)

def init_database():
    db = Session()

    Base.metadata.create_all(bind=db_engine)
    db.commit()
    


def init_cards():
    db = Session()

    cards = [
        Card(Ranks.two, Colors.clubs, '2C', 2, 2),
        Card(Ranks.two, Colors.diamonds, '2D', 2, 2),
        Card(Ranks.two, Colors.hearts, '2H', 2, 2),
        Card(Ranks.two, Colors.spades, '2S', 2, 2),

        Card(Ranks.three, Colors.clubs, '3C', 3, 3),
        Card(Ranks.three, Colors.diamonds, '3D', 3, 3),
        Card(Ranks.three, Colors.hearts, '3H', 3, 3),
        Card(Ranks.three, Colors.spades, '3S', 3, 3),

        Card(Ranks.four, Colors.clubs, '4C', 4, 4),
        Card(Ranks.four, Colors.diamonds, '4D', 4, 4),
        Card(Ranks.four, Colors.hearts, '4H', 4, 4),
        Card(Ranks.four, Colors.spades, '4S', 4, 4),

        Card(Ranks.five, Colors.spades, '5S', 5, 5),
        Card(Ranks.five, Colors.hearts, '5H', 5, 5),
        Card(Ranks.five, Colors.diamonds, '5D', 5, 5),
        Card(Ranks.five, Colors.clubs, '5C', 5, 5),

        Card(Ranks.six, Colors.spades, '6S', 6, 6),
        Card(Ranks.six, Colors.hearts, '6H', 6, 6),
        Card(Ranks.six, Colors.diamonds, '6D', 6, 6),
        Card(Ranks.six, Colors.clubs, '6C', 6, 6),

        Card(Ranks.seven, Colors.clubs, '7C', 7, 7),
        Card(Ranks.seven, Colors.spades, '7S', 7, 7),
        Card(Ranks.seven, Colors.hearts, '7H', 7, 7),
        Card(Ranks.seven, Colors.diamonds, '7D', 7, 7),

        Card(Ranks.eight, Colors.diamonds, '8D', 8, 8),
        Card(Ranks.eight, Colors.spades, '8S', 8, 8),
        Card(Ranks.eight, Colors.hearts, '8H', 8, 8),
        Card(Ranks.eight, Colors.clubs, '8C', 8, 8),

        Card(Ranks.nine, Colors.clubs, '9C', 9, 9),
        Card(Ranks.nine, Colors.spades, '9S', 9, 9),
        Card(Ranks.nine, Colors.hearts, '9H', 9, 9),
        Card(Ranks.nine, Colors.diamonds, '9D', 9, 9),

        Card(Ranks.ten, Colors.diamonds, '10D', 10, 10),
        Card(Ranks.ten, Colors.spades, '10S', 10, 10),
        Card(Ranks.ten, Colors.hearts, '10H', 10, 10),
        Card(Ranks.ten, Colors.clubs, '10C', 10, 10),

        Card(Ranks.jack, Colors.clubs, 'JC', 11, 10),
        Card(Ranks.jack, Colors.spades, 'JS', 11, 10),
        Card(Ranks.jack, Colors.hearts, 'JH', 11, 10),
        Card(Ranks.jack, Colors.diamonds, 'JD', 11, 10),

        Card(Ranks.queen, Colors.diamonds, 'QD', 12, 10),
        Card(Ranks.queen, Colors.spades, 'QS', 12, 10),
        Card(Ranks.queen, Colors.hearts, 'QH', 12, 10),
        Card(Ranks.queen, Colors.clubs, 'QC', 12, 10),

        Card(Ranks.king, Colors.clubs, 'KC', 13, 10),
        Card(Ranks.king, Colors.spades, 'KS', 13, 10),
        Card(Ranks.king, Colors.hearts, 'KH', 13, 10),
        Card(Ranks.king, Colors.diamonds, 'KD', 13, 10),

        Card(Ranks.ace, Colors.diamonds, 'AD', 14, 11),
        Card(Ranks.ace, Colors.spades, 'AS', 14, 11),
        Card(Ranks.ace, Colors.hearts, 'AH', 14, 11),
        Card(Ranks.ace, Colors.clubs, 'AC', 14, 11)
    ]

    for card in cards:
        if db.query(Card).filter(Card.image_name == card.image_name).count() == False:
            db.add(card)
            db.commit()
