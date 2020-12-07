
// Constants
var allowed_characters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v",
"w","x","y","z",".",",",":","=",";","?","\"","\\","/","!","^","°","|","&","%","*","+","-","_","~","#","'","(",")",
"0","1","2","3","4","5","6","7","8","9"," "];

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
    var id_pre_input = $('#pre_input');
    var id_pre_cursor = $('#pre_cursor');
    var id_cursor = $('#cursor');

    // Focus input
    id_input.focus();
    $(document).on("click", function() {
        id_input.focus();
    });

    // socket.io
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/');
    socket.on('connect', function() { id_log.html(""); });
    socket.on('user', function(obj) { id_user.text(obj.data); });
    socket.on('machine', function(obj) { id_machine.text(obj.data); });
    socket.on('path', function(obj) { id_path.text(obj.data); });
    socket.on('msg', function(obj) {
        current_app = 'msg';
        append_to_log(obj);
        show_or_hide_pre_input(!obj.show_pre_input);
        window.scrollTo(0,document.body.scrollHeight);
    });
    socket.on('login', function(obj) {
        current_app = 'login_username';
        append_to_log(obj);
        show_or_hide_pre_input(!obj.show_pre_input);
        window.scrollTo(0,document.body.scrollHeight);
    });
    socket.on('invite_user', function(obj) {
        id_log.append(id_pre_input.html() + "<br>");
        current_app = 'accept_invitation';
        user_from = obj.user_from;
        user_to = obj.user_to;
        append_to_log(obj);
        show_or_hide_pre_input(!obj.show_pre_input);
        window.scrollTo(0,document.body.scrollHeight);
    });

    // On Key down
    $(document).on('keydown',function(e) {
        if (e.which == 13) {
            // Enter
            var command = id_input.val();
            id_input.val("");
            id_pre_cursor.html("");
            if (id_pre_input.is(":visible")) {
                id_log.append(id_pre_input.html());
            }
            id_log.append('<span>' + command + '</span><br>');
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
            socket.emit(current_app, {data: command, user_from: user_from, user_to: user_to});
        } else if (e.which == 38 || e.which == 40) {
            // Up and Down arrows
            if (e.which == 38 && cmd_history_pos < cmd_history.length) {
                cmd_history_pos += 1;
                id_input.val(cmd_history[cmd_history.length-cmd_history_pos]);
            }
            else if (e.which == 40 && cmd_history_pos > 1) {
                cmd_history_pos -= 1;
                id_input.val(cmd_history[cmd_history.length-cmd_history_pos]);
            }
            e.preventDefault();
        } else if (e.which == 37 || e.which == 39) {
            if (e.which == 37 && id_pre_cursor.text().length > 0) {
                id_pre_cursor.text(id_pre_cursor.text().slice(0, -1));
            } else if (e.which == 39 && id_pre_cursor.text().length < id_input.val().length) {
                id_pre_cursor.text(id_pre_cursor.text() + "x");
            }
            if (id_pre_cursor.text().length < id_input.val().length) {
                id_cursor.css("opacity", "0.25");
            } else {
                id_cursor.css("opacity", "1");
            }
        }
    });


    id_input.on('input', function() {
        id_pre_cursor.text(id_input.val())
    });


    function append_to_log(obj) {
        var message = parse_message(obj.data);
        id_log.append('<span class="' + obj.classes.join(" ") + '">' + message + '</span>');
        if (obj.new_line == true) {
            id_log.append('<br>');
        }
    }

    function show_or_hide_pre_input(hide) {
        if (hide) {
            id_pre_input.hide();
        } else {
            id_pre_input.show();
        }
    }

    function parse_message(message) {
        message = message.replaceAll(bold, bold_replacer);
        message = message.replaceAll(italic, italic_replacer);
        message = message.replaceAll(url, url_replacer);
        return message;
    }

    setInterval(function(){
        id_cursor.toggleClass("on")
    }, 500);
});




function bold_replacer(match, text, offset, string){
    return "<b>" + text + "</b>";
}
function italic_replacer(match, text, offset, string){
    return "<i>" + text + "</i>";
}
function url_replacer(match, text, offset, string){
    return '<a href="' + text + '" target="_blank">' + text + '</a>';
}
