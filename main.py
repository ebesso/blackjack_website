from init_app import socketio, create_app
import initializer
import os

app = create_app(True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))        
    socketio.run(app, host='0.0.0.0' , port=port)
    