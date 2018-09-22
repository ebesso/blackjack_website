from flask import Blueprint, request, render_template
from . import others

import initializer
from general_handlers import configuration_handler

@others.route('/')
def index():
    return render_template('index.html', website_info=configuration_handler.load('website'))

@others.route('/init')
def init():
    initializer.init()
    return 'initialized'
