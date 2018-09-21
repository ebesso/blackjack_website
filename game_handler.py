from models import Game, Active_card, Card, Status, Ranks, Game_state, User

from deck_handler import init_deck, draw

import os, random, string, json

def init_game(player, bet, db):

    if db.session.query(Game).filter(Game.player == player).count():
        delete_game(db.session.query(Game).filter(Game.player == player).one().id, db)

    cpu_hand_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(45))

    user = db.session.query(User).filter(User.identifier == player).one()
    user.balance -= bet
    print('Removed bet amount from user')

    db.session.add(Game(player, bet, cpu_hand_identifier))
    db.session.commit()
    print('Init game + commited to database')

    return db.session.query(Game).filter(Game.player == player).one().id

def delete_game(gameid, db):
    db.session.query(Game).filter(Game.id == gameid).delete()
    db.session.query(Active_card).filter(Active_card.game_identifier == gameid).delete()

    db.session.commit()

def isIngame(identifier, db):
    print('Validating identifier ' + identifier)

    if db.session.query(Game).filter(Game.player == identifier).count():
        return True
    else:
        return False

def get_cpu_identifier(identifier, db):
    return db.session.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier

def update_table(identifier, db):    
    game = db.session.query(Game).filter(Game.player == identifier).one()

    player_hand = db.session.query(Active_card).filter(Active_card.owner == identifier).all()
    cpu_hand = db.session.query(Active_card).filter(Active_card.owner == game.cpu_hand_identifier).all()

    print('Got hands')

    table_data = {
        'player_cards': [],
        'cpu_cards': [],
        'doubledown': doubledown_valid(identifier, db),
        'bet': db.session.query(Game).filter(Game.player == identifier).one().bet 
    }
    print('Got doubledown and bet status')

    for card in player_hand:
        card_data = {
            'image': db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        table_data['player_cards'].append(card_data)
    
    print('Got player images')
    
    for card in cpu_hand:

        if card.status == Status.visible:
            image_name = db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        else:
            image_name = 'red_back'

        card_data = {
            'image': image_name
        }
        table_data['cpu_cards'].append(card_data)
    
    print('Got cpu images')

    print(table_data)

    return table_data

def calculate_hand(identifier, db):
    
    hand = db.session.query(Active_card).filter(Active_card.owner == identifier).all()

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
    
def get_game_state(identifier, db):
    game = db.session.query(Game).filter(Game.player == identifier).one()

    player_value = calculate_hand(identifier, db)
    cpu_value = calculate_hand(game.cpu_hand_identifier, db)

    player_cards = db.session.query(Active_card).filter(Active_card.owner == identifier).count()
    cpu_cards = db.session.query(Active_card).filter(Active_card.owner == game.cpu_hand_identifier).count()

    print('Player hand ' + str(player_value))
    print('Cpu hand ' + str(cpu_value))

    if player_value > 21:
        current_gamestate = Game_state.player_busted
    elif cpu_value > 21:
        current_gamestate = Game_state.cpu_busted

    elif cpu_value == 21 and cpu_cards == 2:
        current_gamestate = Game_state.cpu_blackjack
    elif player_value == 21 and player_cards == 2:
        current_gamestate = Game_state.player_blackjack

    elif player_value > cpu_value:
        current_gamestate = Game_state.player_lead
    elif player_value < cpu_value:
        current_gamestate = Game_state.cpu_lead

    elif player_value == cpu_value:
        current_gamestate = Game_state.draw
    
    return current_gamestate

def isGameOver(identifier, db):
    game_state = get_game_state(identifier, db)

    if game_state == Game_state.cpu_blackjack or game_state == Game_state.player_blackjack or game_state == Game_state.player_busted:
        return True
    return False

def simulate_cpu(identifier, socketio, db, sid):
    cpu_identifer = db.session.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier

    while True:
        if calculate_hand(cpu_identifer, db) > 16 or get_game_state == Game_state.player_busted:
            break
        else:
            draw(cpu_identifer, Status.visible, db)
            socketio.emit('update_table', json.dumps(update_table(identifier, db)), room=sid)

def finish_game(identifier, db):
    game_data = {
        'player_cards': [],
        'cpu_cards': []
    }

    for card in db.session.query(Active_card).filter(Active_card.owner == identifier).all():
        card_data = {
            'image': db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        game_data['player_cards'].append(card_data)

    for card in db.session.query(Active_card).filter(Active_card.owner == db.session.query(Game).filter(Game.player == identifier).one().cpu_hand_identifier).all():
        card_data = {
            'image': db.session.query(Card).filter(Card.id == card.card_identifier).one().image_name
        }

        game_data['cpu_cards'].append(card_data)
    
    game_state = get_game_state(identifier, db)

    if game_state == Game_state.player_busted:
        game_data['result'] = 'You busted'
    elif game_state == Game_state.cpu_busted:
        game_data['result'] = 'Cpu busted'
    elif game_state == Game_state.cpu_blackjack:
        game_data['result'] = 'Cpu got blackjack'
    elif game_state == Game_state.player_blackjack:
        game_data['result'] = 'You got blackjack'
    elif game_state == Game_state.cpu_lead:
        game_data['result'] = 'Cpu won by points'
    elif game_state == Game_state.player_lead:
        game_data['result'] = 'You won by points'
    elif game_state == Game_state.draw:
        game_data['result'] = 'Draw'
    
    delete_game(db.session.query(Game).filter(Game.player == identifier).one().id, db)

    return game_data
            
def doubledown_valid(identifier, db):
    hand_value = calculate_hand(identifier, db)

    if db.session.query(Active_card).filter(Active_card.owner == identifier).count() == 2 and hand_value > 8 and hand_value < 12:
        return True
    else:
        return False