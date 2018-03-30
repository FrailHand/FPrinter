var authenticated = false;
var current_layer = -2;

busy_div = document.getElementById("busy");
if (busy_div == null) {
    authenticated = true;
}

function ping_server() {
    var pingRequest = new XMLHttpRequest();
    pingRequest.open('GET', "/ping?time=" + (new Date()).getTime(), true);

    pingRequest.onreadystatechange = function () {

        if (pingRequest.readyState == 4 && pingRequest.status == 200) {
            var pingresponse = JSON.parse(pingRequest.response);

            if (pingresponse.valid != authenticated) {
                location.reload(true);
            }
        }
    }
    pingRequest.send();
}

var firstPingRequest = new XMLHttpRequest();
firstPingRequest.open('GET', "/ping?time=" + (new Date()).getTime(), true);

firstPingRequest.onreadystatechange = function () {

    if (firstPingRequest.readyState == 4 && firstPingRequest.status == 200) {
        var pingresponse = JSON.parse(firstPingRequest.response);

        if (pingresponse.valid != authenticated) {
            location.reload(true);
        }

        else {
            var ping_scheduler = setInterval(ping_server, pingresponse.interval * 1000);
        }
    }
}
firstPingRequest.send();

function update_layer_image(layer) {
    current_layer = layer;
    document.getElementById("current-layer").src = ("/layer.png?time=" + (new Date()).getTime())
}

function status_template(status) {
    var template = document.getElementById("printing-status-template").innerHTML;
    template = Mustache.to_html(template, status);
    document.getElementById("printing-status").innerHTML = template;
}

function visual_status_update(status) {
    if (status.in_progress) {

        if (status.current_layer != current_layer) {
            update_layer_image(status.current_layer);
        }

        if (status.paused) {
            status['label-class'] = 'warning';
            status['label-title'] = 'PAUSED';
        }
        else {
            status['label-class'] = 'success';
            status['label-title'] = 'PRINTING';
        }

    }
    else {
        if (current_layer != -1) {
            update_layer_image(-1);
            if (typeof update_status !== 'undefined') {
                update_status();
            }
        }

        status['label-class'] = 'danger';
        status['label-title'] = 'STOPPED';
    }

    if (status['current_layer'] > status['max_layer']) {
        status['current_layer'] = status['max_layer']
    }

    status_template(status);
}

function request_status() {
    var statusRequest = new XMLHttpRequest();
    statusRequest.open('GET', "/status?time=" + (new Date()).getTime(), true);

    statusRequest.onreadystatechange = function () {
        if (statusRequest.readyState == 4 && statusRequest.status == 200) {
            var statusresponse = JSON.parse(statusRequest.response);
            visual_status_update(statusresponse);
        }
    }
    statusRequest.send();
}

var status_scheduler = setInterval(request_status, 1000);
