
from flask import Flask, render_template, session, request

from modules.constants import Constants
from modules.sites import Sites
from modules.cssclasses import CSSClasses
from modules.message import send

connected_users = {}    # "name": room_id
chat_rooms = {}         # "name": users[]


registered_users = {}
registered_users['felix'] = 'test'


def request_username():
    send('login_username', ["username: "], new_line=False, show_pre_input=False)


def request_password():
    send('login_password', ["password: "], new_line=False, show_pre_input=False)


def login(username, password):
    if username in registered_users and registered_users[username] == password:
        session['username'] = username
        session['logged_in'] = True
        connected_users[username] = {'room': request.sid}
        send('user', [username])
        send('msg', ["You are now logged in as " + username + "."])
        return True
    return False


def logout(socket_disconnect=True):

    # If user was not logged in
    if 'username' not in session:
        if not socket_disconnect:
            send('msg', ['You can only log out if you log in first.'])
        return

    # If user was logged in
    username = session["username"]
    print('User "' + username + '" disconnected.')
    send('user', [Constants.UNKNOWN_USER_NAME])
    send('msg', ['You are now logged out.'])

    del session['username']
    del session['logged_in']

    user = connected_users[username]
    for room in chat_rooms:
        if username in chat_rooms["users"]:
            room['users'].remove(user)
            for user in chat_rooms["users"]:
                send('msg', [username + " has disconnected."], [CSSClasses.BLUE], room=user["room"])
            if len(chat_rooms['users']) <= 0:
                chat_rooms.remove(room)
    del connected_users[username]


def set_username(username):
    if 'username' in session:
        send('msg', ["You are already logged in. Exit first."])
        return
    if username in connected_users:
        send('msg', ["The username is already taken."])
        return
    session['username'] = username
    request_password()


def login_with_username(parts):
    if len(parts) > 1:
        set_username(parts[1])
    else:
        request_username()


def list_users():
    from app import send
    send('msg', [
        '**Users**',
        Sites.SEPARATOR_LIGHT,
        ', '.join([connected_user["username"] for connected_user in connected_users]),
        '',
        '**Rooms**',
        Sites.SEPARATOR_LIGHT,
        ', '.join([str([user["username"] for user in shared_room["users"]]) for shared_room in shared_rooms])
    ])


def invite_user(user_from, user_to):

    if user_from is None or user_to is None:
        send('msg', ['Please specify a user you want to invite.'], [CSSClasses.RED])
        return

    user = connected_users[user_to]
    if user is None:
        send('msg', ['User offline. Please check the spelling and if the user is online.'], [CSSClasses.RED])
    else:
        send(
            'invite_user',
            data=[user_from + " invited you. Accept? (y/n)"],
            classes=[CSSClasses.BLUE],
            new_line=True,
            show_pre_input=False,
            room=user["room"],
            user_from=user_from,
            user_to=user_to
        )
        send('msg', ['Invitation sent.'], [CSSClasses.AQUA])


def send_to_chatroom(sender_username, message):
    for chat_room in chat_rooms:
        if sender_username in shared_room["users"]:
            for user in shared_room["users"]:
                if user["username"] != sender_username:
                    send('msg', [sender_username + ": " + message], [CSSClasses.BLUE], room=user["room"])
    send('msg', ["You: " + message])
