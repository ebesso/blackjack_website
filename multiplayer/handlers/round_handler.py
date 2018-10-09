from init_app import db, socketio

from multiplayer.handlers.table_handler import get_current_table, get_turn, send_options, options

from general_handlers.user_handler import identifier_to_steamid 

from models import Active_player, Player_status, Table

def round_over(table_id):
    if db.session.query(Active_player).filter(Active_player.table_id == table_id).filter(Active_player.status == Player_status.active).count():
        return False
    return True

def finish_round(table_id):
    pass

def round_action(identifier):
    steamid = identifier_to_steamid(identifier)

    if get_turn(get_current_table(steamid).id) == None:
        if db.session.query(Active_player).filter(Active_player.steamid == steamid).filter(Active_player.bet != None).count():
            print('All bets completed')

            table = get_current_table(steamid)
            table.player_turn = 0

            db.session.commit()
        else:
            print('Sending bet option')
            for player in db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.bet == None).all():
                send_options(player.steamid, options.bet)
    
    elif round_over(get_current_table(steamid).id):
        finish_round(get_current_table(steamid).id)
    
    elif db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == False).count():
        players = db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == False).all()

        send_options(players[0].steamid, options.play)
    
    elif db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == False).count() == False:
        for player in db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == True):
            player.has_played = False
            db.session.commit()
        
        table = get_current_table(steamid)
        table.player_turn += 1
        db.session.commit()

