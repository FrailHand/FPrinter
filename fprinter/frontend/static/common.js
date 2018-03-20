var authenticated = false;

busy_div = document.getElementById("busy");
if(busy_div == null){
    authenticated = true;
}

function ping_server(){
    var pingRequest = new XMLHttpRequest();
    pingRequest.open('GET', "/ping?time="+(new Date()).getTime(), true);

    pingRequest.onreadystatechange = function() {

        if (pingRequest.readyState == 4 && pingRequest.status == 200){
            var response = JSON.parse(pingRequest.response);

            if (response.valid != authenticated){
                location.reload(true);
            }
        }
    }

    pingRequest.send();
}

var ping_scheduler =  setInterval(ping_server, 1000);
