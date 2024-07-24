# server.py
from flask import Flask
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='gevent')

@socketio.on('message')
def handle_message(msg):
    print(f'Received message: {msg}')
    send('Hi!')

if __name__ == '__main__':
    socketio.run(app, debug=True)
