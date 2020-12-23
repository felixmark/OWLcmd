import logging
import time
import subprocess

from flask import Flask, render_template, session, send_from_directory
from flask_socketio import SocketIO, emit
from sys import platform as _platform

from modules.constants import *
from modules.cssclasses import *
from modules.message import *
from modules.sleep import *
from modules.user_handler import *
from modules.execute import *


# =================================================== FLASK SETUP ===================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'somesecretiguess'
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=Constants.PING_TIMEOUT, ping_interval=Constants.PING_INTERVAL)


@socketio.on('connect')
def handle_new_connection():
    print('New connection.')
    send('user', [Constants.UNKNOWN_USER_NAME])
    send('machine', [Constants.MACHINE_NAME])
    send('path', ['/'])
    send('msg', Sites.get_site("asciiart.txt"), [CSSClasses.BRIGHT])
    send('msg', Sites.get_site("greeting.txt"))
    send('msg', Sites.get_site("help.txt"))


@socketio.on('disconnect')
def handle_delete_connection():
    logout()


@socketio.on('keep_alive')
def handle_keep_alive(obj):
    send('keep_alive', [])


@socketio.on('login_username')
def handle_message(obj):
    set_username(obj['data'])


@socketio.on('login_password')
def handle_message(obj):
    login(session['username'], obj['data'])


@socketio.on('accept_invitation')
def handle_message(obj):
    command = obj["data"]
    user_from = connected_users[obj["user_from"]]
    user_to = connected_users[obj["user_to"]]
    if command != "y" and command != "Y":
        send('msg', ['Invitation rejected.'], [CSSClasses.BLUE])
        send('msg', ['Your invitation got rejected.'], [CSSClasses.BLUE], room=user_from["room"])
    else:
        send('msg', ['Invitation accepted.'], [CSSClasses.BLUE])
        send('msg', ['Your invitation was accepted.'], [CSSClasses.BLUE], room=user_from["room"])
        send('user', [user_from["username"] + ">" + user_to["username"]], room=user_from["room"])
        send('user', [user_to["username"] + ">" + user_from["username"]], room=user_to["room"])
        chat_rooms.append({"users": [user_from, user_to]})


user_folder = 'user_folders'


@socketio.on('msg')
def handle_message(obj):
    if 'data' in obj:
        command = obj["data"].encode('latin-1').decode('utf-8')
        parts = str(command).split(" ")
        print("Parts: " + str(parts))

        # NOT LOGGED IN COMMANDS
        if command == "":
            pass
        elif command == "help":
            send('msg', Sites.get_site("help.txt"))
        elif command == "info":
            send('msg', Sites.get_site("info.txt"))
        elif command.startswith("login"):
            login_with_username(parts)

        # LOGGED IN COMMANDS
        elif command == "ls":
            if 'logged_in' in session and session['logged_in']:
                if 'win' in _platform:
                    execute('cd' + user_folder + '/' + session['username'] + ' & ' + 'dir')
                else:
                    execute('ls')
            else:
                send('msg', ['You have to be logged in to perform this action.'], classes=[CSSClasses.RED])
        elif command == "users":
            list_users()
        elif command == "exit":
            logout()
        elif command.startswith('sleep'):
            cmd_sleep(parts)

        # More complex functions
        elif command.startswith("invite"):
            if "username" in session and len(parts) > 1:
                invite_user(session["username"], parts[1])
            elif "username" not in session:
                send('msg', ['Please log in to invite a user.'], [CSSClasses.RED])
            elif len(parts) <= 1:
                send('msg', ['Please specify a user you want to invite.'], [CSSClasses.RED])
        elif command.startswith("msg"):
            if len(parts) > 1 and "username" in session:
                message = str(command).replace("msg ", "")
                send_to_chatroom(session["username"], message)
        else:
            send('msg', ['Command *' + command + '* not found. Please execute *help* for a list of available commands.'])


# =================================================== ROUTES ===================================================
@app.route('/')
def index():
    return render_template('index.html', website_title=Constants.WEBSITE_TITLE)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'img/terminal.ico')


# =================================================== MAIN ===================================================
if __name__ == '__main__':
    socketio.run(app, host=Constants.HOST, debug=Constants.DEBUG, port=Constants.PORT)
