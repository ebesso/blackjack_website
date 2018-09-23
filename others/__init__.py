from flask import Blueprint

others = Blueprint('others', __name__, template_folder='templates')

from . import other_events, other_routes, user_login