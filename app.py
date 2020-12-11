import logging
import time

from flask import Flask, render_template, session, send_from_directory
from flask_socketio import SocketIO, emit

from modules.constants import Constants
from modules.css_classes import CSS_classes
from modules.sites import Sites
from modules.user_handler import disconnect_user, login_with_username, shared_rooms, send_login_username, list_users, \
    invite_user, send_to_shared_room, get_user_by_name


# =================================================== FLASK SETUP ===================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'somesecretiguess'
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=Constants.PING_TIMEOUT, ping_interval=Constants.PING_INTERVAL)


def send(msg_type, data=[], classes=[], new_line=True, show_pre_input=True, room=None, user_from="", user_to=""):
    print("SEND: " + str(data))
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


@socketio.on('connect')
def handle_new_connection():
    print('New connection.')
    send('user', [Constants.UNKNOWN_USER_NAME])
    send('machine', [Constants.MACHINE_NAME])
    send('path', ['/'])
    send('msg', Sites.get_site("asciiart.txt"), [CSS_classes.BLUE, CSS_classes.ASCII_ART])
    send('msg', Sites.get_site("greeting.txt"))
    send('msg', Sites.get_site("help.txt"))


@socketio.on('disconnect')
def handle_delete_connection():
    disconnect_user()


@socketio.on('login_username')
def handle_message(obj):
    login_with_username(obj['data'], True)


@socketio.on('accept_invitation')
def handle_message(obj):
    command = obj["data"]
    user_from = get_user_by_name(obj["user_from"])
    user_to = get_user_by_name(obj["user_to"])
    if command != "y" and command != "Y":
        send('msg', ['Invitation rejected.'], [CSS_classes.BLUE])
        send('msg', ['Your invitation got rejected.'], [CSS_classes.BLUE], room=user_from["room"])
    else:
        send('msg', ['Invitation accepted.'], [CSS_classes.BLUE])
        send('msg', ['Your invitation was accepted.'], [CSS_classes.BLUE], room=user_from["room"])
        send('user', [user_from["username"] + ">" + user_to["username"]], room=user_from["room"])
        send('user', [user_to["username"] + ">" + user_from["username"]], room=user_to["room"])
        shared_rooms.append({"users": [user_from, user_to]})


@socketio.on('msg')
def handle_message(obj):
    if 'data' in obj:
        command = obj["data"].encode('latin-1').decode('utf-8')
        parts = str(command).split(" ")
        print("Parts: " + str(parts))

        if command == "":
            pass
        elif command == "help":
            send('msg', Sites.get_site("help.txt"))
        elif command == "info":
            send('msg', Sites.get_site("info.txt"))
        elif command == "list" or command == "ls":
            list_users()
        elif len(parts) > 0 and parts[0] == "sleep":
            try:
                sleep_time = float(parts[1])
                time.sleep(sleep_time)
                send('msg',[])
            except Exception:
                send('msg',['Please specify the time you want to sleep in seconds.'])

        # More complex functions:
        elif command.startswith("login"):
            login_with_username(parts)
        elif command.startswith("invite"):
            if "username" in session and len(parts) > 1:
                invite_user(session["username"], parts[1])
            elif "username" not in session:
                send('msg', ['Please log in to invite a user.'], [CSS_classes.RED])
            elif len(parts) <= 1:
                send('msg', ['Please specify a user you want to invite.'], [CSS_classes.RED])
        elif command == "exit":
            disconnect_user()
        elif command.startswith("msg"):
            if len(parts) > 1 and "username" in session:
                message = str(command).replace("msg ", "")
                send_to_shared_room(session["username"], message)
        else:
            send('msg', ['Command *' + command + '* not found. Please execute *help* for a list of available commands.'])


# =================================================== ROUTES ===================================================
@app.route('/')
def index():
    return render_template('index.html',
        website_title=Constants.WEBSITE_TITLE
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'img/terminal.ico')


# =================================================== MAIN ===================================================
if __name__ == '__main__':
    socketio.run(app, debug=Constants.DEBUG, port=Constants.PORT)
