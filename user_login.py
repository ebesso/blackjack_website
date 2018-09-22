from flask import Blueprint, make_response, redirect
from init_app import oid

from general_handlers.user_handler import authorize_user

user_login = Blueprint('user_login', __name__)


@user_login.route('/login', methods=['GET'])
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