

class Messages(object):
    SEPARATOR_BOLD = "="*80
    SEPARATOR_LIGHT = "-"*80

    WELCOME_MESSAGE = [
" ______  __     __  __            .___,       ______  __    __  _____    ",
"/\  __ \/\ \  _ \ \/\ \        ___(o.o)___   /\  ___\/\ \"-./  \/\  __-.  ",
"\ \ \/\ \ \ \/ \".\ \ \ \____   `\"-\\._./-\"'   \ \ \___\ \ \-./\ \ \ \/\ \ ",
" \ \_____\ \__/\".~\_\ \_____\      ^ ^        \ \_____\ \_\ \ \_\ \____- ",
"  \/_____/\/_/   \/_/\/_____/                  \/_____/\/_/  \/_/\/____/    v1.0",
        SEPARATOR_BOLD
    ]

    INFO_MESSAGE = [
        "Info",
        SEPARATOR_LIGHT,
        "**This site is powered by:**",
        "Socket.IO                                   https://socket.io",
        "FiraCode Font                               https://github.com/tonsky/FiraCode",
        "Gruvbox Color Scheme                        https://github.com/morhetz/gruvbox",
        "JQuery                                      https://jquery.com",
        "Flask                                       https://palletsprojects.com/p/flask",
        "",
        "**Contact:**",
        "Felix Mark",
        "felix.mark@hotmail.com",
        "Keesgasse 4, 8010 Graz, Austria"
    ]

    HELP_MESSAGE = [
        "**Help**",
        SEPARATOR_LIGHT,
        "info                                              Show website and contact info.",
        "list                                       List all online users and room count.",
        "login *username*                                     Login with username if given.",
        "invite *username*                                   Invite another user to a room.",
        "msg *message*                            Write a message to everyone in your room.",
        "help                                                          View this message."
    ]