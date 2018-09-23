from sqlalchemy import Column, String, Integer, Enum, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
import enum, string, random

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

class Game_state(enum.Enum):
    player_busted = 1
    cpu_busted = 2

    player_blackjack = 3
    cpu_blackjack = 4

    player_lead = 5
    cpu_lead = 6

    draw = 7

class Status(enum.Enum):
    visible = 1
    hidden = 2

class Player_status(enum.Enum):
    stand = 1
    active = 2

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
    bet = Column('bet', Float, nullable=False)

    cpu_hand_identifier = Column('cpu_hand_identifier', String, unique=True)

    def __init__(self, player, bet, cpu_hand_identifier):
        self.player = player
        self.bet = bet
        self.cpu_hand_identifier = cpu_hand_identifier

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

class Table(Base):
    __tablename__ = 'tables'

    id = Column('id', Integer, primary_key=True)

    identifier = Column('identifer', String, unique=True)
    player_turn = Column('player_turn', Integer)
    deck_identifer = Column('deck_identifier', String, unique=True)

    def __init__(self):
        self.identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.deck_identifer = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

class Active_player(Base):
    __tablename__ = 'active_players'

    id = Column('id', Integer, primary_key=True)

    steamid = Column('steamid', String, unique=True)
    table_id = Column('table_id', Integer)
    session_id = Column('session_id', String)

    bet = Column('bet', Float)

    status = Column('status', Enum(Player_status))
    status_string = Column('status_string', String, nullable=False)

    def __init__(self, steamid, table_id):
        self.steamid = steamid
        self.table_id = table_id
        self.status_string = 'Waiting'

class Empty(object):
    def __getattr__(self, prop):
        return self.__dict__[prop]
    def __setattr__(self, prop, val):
        self.__dict__[prop] = val