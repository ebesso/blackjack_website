from flask import Blueprint

singleplayer = Blueprint('single player bp', __name__, 'templates/')

from . import single_player_events, single_player_routes