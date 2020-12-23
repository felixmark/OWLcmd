from flask_socketio import SocketIO, emit


def send(msg_type, data=[], classes=[], new_line=True, show_pre_input=True, room=None, user_from="", user_to=""):
    if len(data) <= 1:
        print("SEND: " + str(data))
    else:
        print("SEND: Multiple lines...")
    if room is not None:
        emit(msg_type, {
            'data': data,
            'classes': classes,
            'new_line': new_line,
            'user_from': user_from,
            'user_to': user_to,
            'show_pre_input': show_pre_input
        }, room=room)
    else:
        emit(msg_type, {
            'data': data,
            'classes': classes,
            'new_line': new_line,
            'user_from': user_from,
            'user_to': user_to,
            'show_pre_input': show_pre_input
        })