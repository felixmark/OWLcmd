
from flask import Flask, render_template, session, request
from modules.sites import Sites
from modules.css_classes import CSS_classes

connected_users = []    # {username, room}
shared_rooms = []       # {users}


def get_user_by_name(username):
    for user in connected_users:
        if user["username"] == username:
            return user
    return None


def is_username_taken(username):
    return get_user_by_name(username) is not None


def send_login_username():
    from main import send
    send('login', "username: ", [], False, False)


def disconnect_user(username):
    from main import send
    print('Disconnecting user "' + username + '".')
    user = get_user_by_name(username)
    connected_users.remove(user)
    for shared_room in shared_rooms:
        if user in shared_room["users"]:
            for user in shared_room["users"]:
                if user["username"] != username:
                    send('msg', username + " has disconnected.", [CSS_classes.BLUE], room=user["room"])
                    send('user', user["username"], room=user["room"])
                    shared_rooms.remove(shared_room)


def login_with_username(obj):
    from main import send
    if 'data' in obj:
        username = obj['data']

        if len(username) > 16:
            send('msg', "The username has to be 16 or less characters long.")
            return
        if 'username' in session:
            send('msg', "You are already logged in. Log out first.")
            return
        if is_username_taken(username):
            send('msg', "The username is already taken.")
            return

        session['username'] = username
        connected_users.append({"username": username, "room": request.sid})
        send('user', username)
        send('msg', "You are now logged in as " + username + ".")


def list_users():
    from main import send
    send('msg', '**Users**')
    send('msg', Sites.SEPARATOR_LIGHT)
    for user in connected_users:
        send('msg', user["username"])
    send('msg', " ")
    send('msg', '**Rooms**')
    send('msg', Sites.SEPARATOR_LIGHT)
    for room in shared_rooms:
        send('msg', str([user["username"] for user in room["users"]]))


def invite_user(user_from, user_to):
    from main import send

    if user_from is None or user_to is None:
        return

    user = get_user_by_name(user_to)
    send(
        'invite_user',
        data=user_from + " invited you. Accept? (y/n)",
        classes=[CSS_classes.BLUE],
        new_line=True,
        show_pre_input=False,
        room=user["room"],
        user_from=user_from,
        user_to=user_to
    )
    send('msg', 'Invitation sent.', [CSS_classes.BLUE])


def send_to_shared_room(sender_username, message):
    from main import send
    sender = get_user_by_name(sender_username)
    for shared_room in shared_rooms:
        if sender in shared_room["users"]:
            for user in shared_room["users"]:
                if user["username"] != sender_username:
                    send('msg', sender_username + ": " + message, [CSS_classes.BLUE], room=user["room"])
    send('msg', "You: " + message, [CSS_classes.BLUE])
