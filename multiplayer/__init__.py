from flask import Blueprint

multiplayer = Blueprint('multiplayer bp', __name__, template_folder='templates')

from . import routes, events