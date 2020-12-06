import socketio


@socketio.on('login_username')
def handle_message(obj):
    if 'data' in obj:
        username = obj['data']
