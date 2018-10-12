from init_app import db, socketio

from multiplayer.handlers.table_handler import get_current_table, get_turn, send_options, options, update_table

from general_handlers.user_handler import identifier_to_steamid 

from models import Active_player, Player_status, Table

def round_over(table_id):
    if db.session.query(Active_player).filter(Active_player.table_id == table_id).filter(Active_player.status == Player_status.active).count():
        return False
    return True

def finish_round(table_id):
    table = db.session.query(Table).filter(Table.id == table_id).one()
    table.player_turn = None
    db.session.commit()

def round_action(identifier):
    steamid = identifier_to_steamid(identifier)

    if get_turn(get_current_table(steamid).id) == None:
        if db.session.query(Active_player).filter(Active_player.steamid == steamid).filter(Active_player.bet != None).count():
            print('All bets completed')

            table = get_current_table(steamid)
            table.player_turn = 0

            db.session.commit()

            round_action(identifier)
        else:
            print('Sending bet option')
            for player in db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.bet == None).all():
                send_options(player.steamid, options.bet)
    
    elif round_over(get_current_table(steamid).id):
        print('Round over')
        finish_round(get_current_table(steamid).id)
    
    elif db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == False).filter(Active_player.status == Player_status.active).count():
        print('Sending play requests to players')
        players = db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == False).all()

        send_options(players[0].steamid, options.play)
    
    elif db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == True).filter(Active_player.status == Player_status.active).count():
        print('All players have played')
        for player in db.session.query(Active_player).filter(Active_player.table_id == get_current_table(steamid).id).filter(Active_player.has_played == True).all():
            player.has_played = False
            db.session.commit()
        
        table = get_current_table(steamid)
        table.player_turn += 1
        db.session.commit()
    
    else:
        print('No action required')
    
    update_table(identifier)