function move(move_id) {
    window.location.replace(window.location.href + "/move/" + move_id)
}

function post() {
    let message = document.getElementById("chat-input").value
    if(message)
        window.location.replace(window.location.href + "/post/" + message);
}

function timeToString(time) {
    let diffInHrs = time / 3600000;
    let hh = Math.floor(diffInHrs);

    let diffInMin = (diffInHrs - hh) * 60;
    let mm = Math.floor(diffInMin);

    let diffInSec = (diffInMin - mm) * 60;
    let ss = Math.floor(diffInSec);

    let formattedHH = hh.toString().padStart(2, "0");
    let formattedMM = mm.toString().padStart(2, "0");
    let formattedSS = ss.toString().padStart(2, "0");

    return `${formattedHH}:${formattedMM}:${formattedSS}`;
}

/*
async function timer() {
    start_time = Date.now() - time;
    while(1) {
        time = Date.now() - start_time;
        document.getElementById("timer").innerHTML = timeToString(time);
    }
}

timer_job = timer()
*/
