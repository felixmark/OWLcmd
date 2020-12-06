import logging
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

from messages import Messages
from classes import Classes
from user_handler import send_login_username, login_with_username, disconnect_user, list_users, invite_user, \
    get_user_by_name, shared_rooms, send_to_shared_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'somesecretiguess'
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app, ping_timeout=10, ping_interval=5)


def parse_parameters(command):
    return str(command).split(" ")[1:]


def send(msg_type, data="", classes=[], new_line=True, show_pre_input=True, room=None, user_from="", user_to=""):
    print("SEND: " + data)
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


def send_all(msg_type, str_arr, classes=[], new_line=True, show_pre_input=True):
    for string in str_arr:
        send(msg_type, string, classes, new_line, show_pre_input)


@socketio.on('connect')
def handle_new_connection():
    print('New connection!')
    send('user', 'unknown')
    send('machine', 'ghostfox.de')
    send('path', '/')
    send('msg', 'Connection established.')
    send_all('msg', Messages.WELCOME_MESSAGE, [Classes.BLUE])
    send_all('msg', Messages.HELP_MESSAGE)


@socketio.on('disconnect')
def handle_delete_connection():
    if "username" in session:
        disconnect_user(session["username"])


@socketio.on('login_username')
def handle_message(obj):
    login_with_username(obj)


@socketio.on('accept_invitation')
def handle_message(obj):
    command = obj["data"]
    user_from = get_user_by_name(obj["user_from"])
    user_to = get_user_by_name(obj["user_to"])
    if command != "y" and command != "Y":
        send('msg', 'Invitation rejected.', [Classes.BLUE])
        send('msg', 'Your invitation got rejected.', [Classes.BLUE], room=user_from["room"])
    else:
        send('msg', 'Invitation accepted.', [Classes.BLUE])
        send('msg', 'Your invitation was accepted.', [Classes.BLUE], room=user_from["room"])
        send('user', user_from["username"] + ">" + user_to["username"], room=user_from["room"])
        send('user', user_to["username"] + ">" + user_from["username"], room=user_to["room"])
        shared_rooms.append({"users": [user_from, user_to]})


@socketio.on('msg')
def handle_message(obj):
    print('RECV: ' + str(obj))

    if 'data' in obj:
        command = obj["data"]
        parameters = parse_parameters(command)
        print("Parameters: " + str(parameters))

        if command == "":
            pass
        elif command.startswith("login"):
            if len(parameters) >= 1:
                login_with_username({'data': parameters[0]})
            else:
                send_login_username()
        elif command == "list":
            list_users()
        elif command.startswith("invite"):
            if len(parameters) >= 1:
                invite_user(session["username"], parameters[0])
        elif command == "help":
            send_all('msg', Messages.HELP_MESSAGE)
        elif command == "info":
            send_all('msg', Messages.INFO_MESSAGE)
        elif command.startswith("msg"):
            if len(parameters) >= 1 and "username" in session:
                message = str(command).replace("msg ", "")
                send_to_shared_room(session["username"], message)
        else:
            send('msg', 'Command *' + command + '* not found. Please execute *help* for a list of available commands.')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=14159, debug=True)
