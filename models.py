from sqlalchemy import Column, String, Integer, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class Colors(enum.Enum):
    spades = 1
    hearts = 2
    diamonds = 3
    clubs = 4

class Ranks(enum.Enum):
    two = 1
    three = 2
    four = 3
    five = 6
    six = 7
    seven = 8
    eight = 9
    nine = 10
    ten = 11
    
    jack = 12
    queen = 14
    king = 15

    ace = 16

class Status(enum.Enum):
    visible = 1
    hidden = 2

class Card(Base):
    __tablename__ = 'cards'

    id = Column('id', Integer, primary_key=True)

    rank = Column('type', Enum(Ranks), nullable=False)
    color = Column('color', Enum(Colors), nullable=False)

    image_name = Column('image_name', String, nullable=False, unique=True)

    value = Column('value', Integer, nullable=False)

    blackjack_value = Column('blackjack_value', Integer, nullable=False)

    def __init__(self, rank, color, image_name, value, blackjack_value):
        self.rank = rank
        self.color = color
        self.image_name = image_name

        self.value = value
        self.blackjack_value = blackjack_value

class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)

    identifier = Column('identifier', String, unique=True)
    steamid = Column('steamid', String, unique=True)

    balance = Column('balance', Integer, nullable=False)

    def __init__(self, steamid, balance, identifier):
        self.identifier = identifier
        self.steamid = steamid
        self.balance = balance

class Game(Base):
    __tablename__ = 'game'

    id = Column('id', Integer, primary_key=True)

    player = Column('player', String, unique=True)
    bet = Column('bet', Integer, nullable=False)

    player_hand_identifier = Column('player_hand_identifier', String, unique=True)
    cpu_hand_identifier = Column('cpu_hand_identifier', String, unique=True)

    active = Column('active', Boolean, nullable=False)

    def __init__(self, player, bet, player_hand_identifier, cpu_hand_identifier):
        self.player = player
        self.bet = bet
        self.player_hand_identifier = player_hand_identifier
        self.cpu_hand_identifier = cpu_hand_identifier
        self.active = True

class Active_card(Base):
    __tablename__ = 'active_cards'

    id = Column('id', Integer, primary_key=True)

    game_identifier = Column('game_identifier', Integer, nullable=False)
    card_identifier = Column('card_identifier', Integer, nullable=False)

    status = Column('status', Enum(Status))

    owner = Column('owner', String)

    def __init__(self, card_identifier, game_identifier):
        self.card_identifier = card_identifier
        self.game_identifier = game_identifier

class Empty(object):
    def __getattr__(self, prop):
        return self.__dict__[prop]
    def __setattr__(self, prop, val):
        self.__dict__[prop] = val