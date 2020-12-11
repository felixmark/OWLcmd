
// Constants
var fill_string = new Array(256).join('+');

// Regex
var bold = /\*\*([^\*]+)\*\*/gi;
var italic = /\*([^\*]+)\*/gi;
var url = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi;


// When document loaded
$(document).ready(function(){
    // Variables
    var current_app = "msg";
    var user_from = "", user_to = "";
    var cmd_history = [];
    var cmd_history_pos = 0;

    var id_user = $('#user');
    var id_machine = $('#machine');
    var id_path = $('#path');
    var id_log = $('#log');
    var id_input = $('#input');
    var id_prompt = $('#prompt');
    var id_pre_cursor = $('#pre_cursor');
    var id_cursor = $('#cursor');

    // Focus input
    id_input.focus();
    $(document).on("click", function() {
        id_input.focus();
    });


    // socket.io
    var socket = io.connect('ws://' + document.domain + ':' + location.port + '/', {
        transports: ['polling', 'websocket']
    });
    socket.on('connect', function() { /* You are now connected. */ });
    socket.on('user', function(obj) { id_user.text(obj.data); });
    socket.on('machine', function(obj) { id_machine.text(obj.data); });
    socket.on('path', function(obj) { id_path.text(obj.data); });
    socket.on('msg', function(obj) {
        current_app = 'msg';
        append_to_log(obj);
        show_prompt(obj.show_pre_input);
        window.scrollTo(0,document.body.scrollHeight);
    });
    socket.on('login', function(obj) {
        current_app = 'login_username';
        append_to_log(obj);
        show_prompt(obj.show_pre_input);
        window.scrollTo(0,document.body.scrollHeight);
    });
    socket.on('invite_user', function(obj) {
        id_log.append(id_prompt.html() + "<br>");
        current_app = 'accept_invitation';
        user_from = obj.user_from;
        user_to = obj.user_to;
        append_to_log(obj);
        show_prompt(obj.show_pre_input);
        window.scrollTo(0,document.body.scrollHeight);
    });


    // On Key down
    $(document).on('keydown',function(e) {
        if (e.which == 13) {
            // Enter
            var command = parse_message(id_input.val(), false);
            id_input.val("");
            id_pre_cursor.html("");
            if (!command.startsWith("msg ")) {
                if (id_prompt.is(":visible")) {
                    id_log.append(id_prompt.html());
                }
                id_log.append('<span>' + parse_message(command, false) + '</span><br>');
            }
            cmd_history.push(command);
            cmd_history_pos = 0;

            // Handle some commands offline
            if (command === "") {
                return;
            }
            if (command === "clear" || command === "cls") {
                id_log.html("");
                return;
            }

            // Send command
            if (user_from === "" || user_to === "") {
                socket.emit(current_app, { data: command });
            } else {
                socket.emit(current_app, { data: command, user_from: user_from, user_to: user_to });
            }
            show_prompt(false);
        } else if (e.which == 38 || e.which == 40) {
            // Up and Down arrows
            if (e.which == 38 && cmd_history_pos < cmd_history.length) {
                cmd_history_pos += 1;
                id_input.val(cmd_history[cmd_history.length-cmd_history_pos]);
            }
            else if (e.which == 40 && cmd_history_pos > 0) {
                cmd_history_pos -= 1;
                if (cmd_history_pos > -1) {
                    id_input.val(cmd_history[cmd_history.length-cmd_history_pos]);
                } else {
                    id_input.val("");
                }
            }
            input_changed();
            e.preventDefault();
        } else if (e.which == 37 || e.which == 39) {
            // Left and right arrows
            input_position = id_input.getCursorPosition()
            if (e.which == 37) {
                if (input_position > 0) input_position -= 1;
                id_pre_cursor.text(fill_string.substring(0, input_position));
            } else if (e.which == 39) {
                if (input_position < id_input.val().length) input_position += 1;
                id_pre_cursor.text(fill_string.substring(0, input_position));
            }
            if (input_position < id_input.val().length) {
                id_cursor.css("opacity", "0.25");
            } else {
                id_cursor.css("opacity", "1");
            }
            prevent_cursor_blinking();
        }
    });

    id_input.on('keydown', input_changed);
    id_input.on('input', input_changed);

    function append_to_log(obj) {
        obj.data.forEach(message => {
            message = parse_message(message, true);
            id_log.append('<span class="' + obj.classes.join(" ") + '">' + message + '</span>');
            if (obj.new_line == true) {
                id_log.append('<br>');
            }
        });
    }

    function show_prompt(show_prompt) {
        if (show_prompt) {
            id_prompt.show();
        } else {
            id_prompt.hide();
        }
    }

    function input_changed() {
        var id_pre_cursor = $('#pre_cursor');
        var id_input = $('#input');
        id_pre_cursor.text(fill_string.substring(0, id_input.getCursorPosition()));
        prevent_cursor_blinking();
    }

    function parse_message(message, receiving=true) {
        message = message.replaceAll("<","&lt;").replaceAll(">","&gt;");
        if (receiving) {
            message = message.replaceAll(url, url_replacer);
            message = message.replaceAll(bold, bold_replacer);
            message = message.replaceAll(italic, italic_replacer);
        } else {
            message = message.replaceAll("*","&ast;");
        }
        return message;
    }

    function prevent_cursor_blinking() {
        clearInterval(cursor_blink);
        id_cursor.addClass("on");
        make_cursor_blink();
    }
    function make_cursor_blink() {
        cursor_blink = setInterval(function(){
            id_cursor.toggleClass("on")
        }, 500);
    }
    make_cursor_blink();
});




function bold_replacer(match, text, offset, string){
    return "<b>" + text + "</b>";
}
function italic_replacer(match, text, offset, string){
    return "<i>" + text + "</i>";
}
function url_replacer(match, text, offset, string){
    text_lower = text.toLowerCase()
    if (text_lower.endsWith('.jpg') || text_lower.endsWith('.png') || text_lower.endsWith('.gif')) {
        return '<img src="' + text + '"></img>';
    } else {
        return '<a href="' + text + '" target="_blank">' + text + '</a>';
    }
}

(function($) {
    $.fn.getCursorPosition = function() {
        var input = this.get(0);
        if (!input) return; // No (input) element found
        if ('selectionStart' in input) {
            // Standard-compliant browsers
            return input.selectionStart;
        } else if (document.selection) {
            // IE
            input.focus();
            var sel = document.selection.createRange();
            var selLen = document.selection.createRange().text.length;
            sel.moveStart('character', -input.value.length);
            return sel.text.length - selLen;
        }
    }
})(jQuery);