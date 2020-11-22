function move(move_id) {
    window.location.replace(window.location.href + "/move/" + move_id)
}

function post() {
    let message = document.getElementById("chat-input").value
    if(message)
        window.location.replace(window.location.href + "/post/" + message);
}
