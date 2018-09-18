from flask import Flask, Blueprint, current_app, redirect, make_response
from flask_openid import OpenID
from flask_login import login_user, logout_user, login_required, current_user

from user_handler import authorize_user

user_login_bp = Blueprint('user_login', __name__, template_folder='templates')

app = Flask(__name__)

with app.app_context():
    oid = OpenID(current_app)

@user_login_bp.route('/login', methods=['GET'])
@oid.loginhandler
def open_id_login():
    return oid.try_login('http://steamcommunity.com/openid')

@oid.after_login
def login_handling(steam_response):
    steamid = steam_response.identity_url.split('/')[5]

    identifier = authorize_user(steamid)

    resp = make_response(redirect('/'))
    resp.set_cookie('identifier', identifier)

    return resp