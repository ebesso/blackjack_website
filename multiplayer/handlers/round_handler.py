from init_app import db

from multiplayer.handlers.table_handler import get_current_table, get_turn
from general_handlers.user_handler import identifier_to_steamid 

from models import Active_player, Player_status

def round_over(table_id):
    if db.session.query(Active_player).filter(Active_player.table_id == table_id).count() > 2 and db.session.query(Active_player).filter(Active_player.table_id == table_id).filter(Active_player.status == Player_status.active).count > 0:
        return True
    return False

def finish_round():
    pass


def next_turn(identifier):
    if round_over(get_current_table(identifier_to_steamid(identifier)).id):
        finish_round

    table = get_current_table(identifier_to_steamid(identifier))
    players = db.session.query(Active_player).filter(Active_player.table_id == table.id).all()

    if table.player_turn == None:
        table.player_turn = 0
        db.session.commit()
        return

    new_turn = table.player_turn

    while True:
        new_turn += 1

        if new_turn > len(players):
            new_turn = 0

        if players[new_turn].status == Player_status.active:
            table.player_turn = new_turn
            db.session.commit()
            return

def get_player_turn_sid(table_id):
    players = db.session.query(Active_player).filter(Active_player.status == Player_status.active).filter(Active_player.table_id == table_id).all()
    return players[get_turn(table_id)].session_id
