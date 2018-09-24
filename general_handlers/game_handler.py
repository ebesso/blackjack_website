from models import Game, Active_card, Card, Status, Ranks, Game_state, User
from init_app import db

import os, random, string, json

def calculate_hand(steamid):
    
    hand = db.session.query(Active_card).filter(Active_card.owner == steamid).all()

    hand_value = 0

    contains_ace = False

    for card in hand:
        hand_value += db.session.query(Card).filter(Card.id == card.card_identifier).one().blackjack_value
        if db.session.query(Card).filter(Card.id == card.card_identifier).one().rank == Ranks.ace:
            contains_ace = True
    
    if contains_ace == False:
        return hand_value
    
    if hand_value < 22:
        return hand_value
    
    for card in hand:
        if db.session.query(Card).filter(Card.id == card.card_identifier).one().rank == Ranks.ace:
            hand_value -= 10
            if hand_value < 22:
                return hand_value
    
    return hand_value
    
def doubledown_valid(steamid):
    hand_value = calculate_hand(steamid)

    if db.session.query(Active_card).filter(Active_card.owner == steamid).count() == 2 and hand_value > 8 and hand_value < 12:
        return True
    else:
        return False