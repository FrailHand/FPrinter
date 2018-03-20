var authenticated = -1

function ping_server(){
    var pingRequest = new XMLHttpRequest();
    pingRequest.open('GET', "/ping?time="+(new Date()).getTime(), true);

    pingRequest.onreadystatechange = function() {

        if (pingRequest.readyState == 4 && pingRequest.status == 200){
            var response = JSON.parse(pingRequest.response);

            if (authenticated == -1){
                authenticated = response.valid
            }

            if (response.valid != authenticated){
                location.reload(true);
            }
        }
    }

    pingRequest.send();
}

var ping_scheduler =  setInterval(ping_server, 1000);
