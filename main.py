from flask import Flask
from initializer import init_cards, init_database

from flask_socketio import SocketIO

from user_login import user_login_bp

app = Flask(__name__)

app.secret_key = '123'
app.debug = True

init_database()
init_cards()

app.register_blueprint(user_login_bp)

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(host='0.0.0.0')