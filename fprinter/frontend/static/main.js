function enable_button(id, enable) {
    var button = document.getElementById(id);
    if (enable) {
        button.removeAttribute("disabled");
    }
    else {
        if (!button.hasAttribute("disabled")) {
            button.setAttribute("disabled", "");
        }
    }

}

function enable_upload(enable) {
    enable_button("upload-button", enable);

    var form = document.getElementById("input-svg");
    if (enable) {
        form.removeAttribute("hidden");
    }
    else {
        if (!form.hasAttribute("hidden")) {
            form.setAttribute("hidden", "");
        }
    }
}

function update_status() {

    var httpRequest = new XMLHttpRequest();
    httpRequest.open("GET", "/status?time=" + (new Date()).getTime(), true);

    httpRequest.onreadystatechange = function () {

        if (httpRequest.readyState === 4 && httpRequest.status === 200) {
            var httpresponse = JSON.parse(httpRequest.response);

            if (httpresponse.in_progress) {
                enable_upload(false);

                var template = document.getElementById("file-success-template").innerHTML;
                template = Mustache.to_html(template, httpresponse);
                document.getElementById("alert-upload").innerHTML = template;

                if (httpresponse.ready) {
                    enable_button("start-button", true);
                    enable_button("abort-button", true);
                }
                else {
                    enable_button("start-button", false);
                    enable_button("abort-button", false);
                }

                var pause_button = document.getElementById("start-button");

                if (httpresponse.paused) {
                    pause_button.innerHTML = "resume";

                    pause_button.classList.remove("uk-button-secondary");
                    pause_button.classList.add("uk-button-primary");

                    template = document.getElementById("info-template").innerHTML;
                    template = Mustache.to_html(template, {"info": "Print paused"});
                    document.getElementById("alert-buttons").innerHTML = template;
                }
                else {
                    pause_button.innerHTML = "pause";

                    pause_button.classList.remove("uk-button-primary");
                    pause_button.classList.add("uk-button-secondary");

                    template = document.getElementById("info-template").innerHTML;
                    template = Mustache.to_html(template, {"info": "Print in progress..."});
                    document.getElementById("alert-buttons").innerHTML = template;
                }
            }

            else {
                var start_button = document.getElementById("start-button");
                start_button.innerHTML = "start";
                start_button.classList.remove("uk-button-secondary");
                start_button.classList.add("uk-button-primary");

                enable_button("abort-button", false);

                enable_upload(true);

                if (httpresponse.name !== "") {
                    template = document.getElementById("file-success-template").innerHTML;
                    template = Mustache.to_html(template, httpresponse);
                    document.getElementById("alert-upload").innerHTML = template;

                    if (httpresponse.ready) {
                        enable_button("start-button", true);
                        template = document.getElementById("info-template").innerHTML;
                        template = Mustache.to_html(template, {"info": "Printer ready"});
                        document.getElementById("alert-buttons").innerHTML = template;
                    }
                    else {
                        enable_button("start-button", false);
                        template = document.getElementById("info-template").innerHTML;
                        template = Mustache.to_html(template, {"info": "Waiting for user"});
                        document.getElementById("alert-buttons").innerHTML = template;
                    }
                }

                else {
                    enable_button("start-button", false);
                    template = document.getElementById("info-template").innerHTML;
                    template = Mustache.to_html(template, {"info": "Upload SVG"});
                    document.getElementById("alert-buttons").innerHTML = template;

                    template = document.getElementById("info-template").innerHTML;
                    template = Mustache.to_html(template, {"info": "Select the svg slices"});
                    document.getElementById("alert-upload").innerHTML = template;
                }

            }

            if (httpresponse.current_layer === httpresponse.max_layer + 1) {
                template = document.getElementById("info-template").innerHTML;
                template = Mustache.to_html(template, {"info": "Print finished!"});
                document.getElementById("alert-buttons").innerHTML = template;
            }

            visual_status_update(httpresponse);
        }
    };
    httpRequest.send();
}

UIkit.upload("#upload-svg", {

    url: "/upload",
    allow: "*.svg",

    completeAll: function (e) {
        var uploadresponse = JSON.parse(e.response);

        if (uploadresponse.valid) {
            update_status();
        }
        else {
            template = document.getElementById("error-template").innerHTML;
            template = Mustache.to_html(template, uploadresponse);
            document.getElementById("alert-upload").innerHTML = template;

            enable_button("start-button", false);
        }
    },

    loadStart: function (e) {
        var bar = document.getElementById("js-progressbar");

        document.getElementById("alert-upload").innerHTML = document.getElementById("progress-template").innerHTML;

        if (bar !== null) {
            bar.max = e.total;
            bar.value = e.loaded;
        }
    },

    progress: function (e) {
        var bar = document.getElementById("js-progressbar");
        bar.max = e.total;
        bar.value = e.loaded;
    },

    fail: function () {
        enable_button("start-button", false);

        var alert_element = document.getElementById("alert-invalid");
        if (alert_element == null) {
            document.getElementById("alert-upload").innerHTML = document.getElementById("invalid-template").innerHTML;
        }

        else {
            alert_element.classList.remove("uk-animation-shake");
            void alert_element.offsetWidth;
            alert_element.classList.add("uk-animation-shake");
        }
    }

});

document.getElementById("start-button").onclick = function () {
    enable_button("start-button", false);

    var button_label = document.getElementById("start-button").innerHTML;
    if (button_label === "start") {

        enable_upload(false);

        var startRequest = new XMLHttpRequest();
        startRequest.open("GET", "/button/start?time=" + (new Date()).getTime(), true);

        startRequest.onreadystatechange = function () {

            if (startRequest.readyState === 4 && startRequest.status === 200) {
                var startresponse = JSON.parse(startRequest.response);

                if (startresponse.valid) {
                    update_status();
                }
                else {
                    var template = document.getElementById("error-template").innerHTML;
                    template = Mustache.to_html(template, startresponse);
                    document.getElementById("alert-buttons").innerHTML = template;

                    enable_upload(true);
                    enable_button("start-button", true);
                }

            }
        };

        startRequest.send();
    }
    else {
        var pauseRequest = new XMLHttpRequest();
        pauseRequest.open("GET", "/button/" + button_label + "?time=" + (new Date()).getTime(), true);

        pauseRequest.onreadystatechange = function () {

            if (pauseRequest.readyState === 4 && pauseRequest.status === 200) {
                var pauseresponse = JSON.parse(pauseRequest.response);

                if (pauseresponse.valid) {
                    update_status();
                }
                else {
                    var template = document.getElementById("error-template").innerHTML;
                    template = Mustache.to_html(template, pauseresponse);
                    document.getElementById("alert-buttons").innerHTML = template;

                    enable_button("start-button", true);
                }
            }
        };
        pauseRequest.send();
    }
};

document.getElementById("abort-button-confirmed").onclick = function () {
    var abortRequest = new XMLHttpRequest();
    abortRequest.open("GET", "/button/abort?time=" + (new Date()).getTime(), true);

    abortRequest.onreadystatechange = function () {

        if (abortRequest.readyState === 4 && abortRequest.status === 200) {
            var abortresponse = JSON.parse(abortRequest.response);
            if (abortresponse.valid) {
                update_status();

                var template = document.getElementById("info-template").innerHTML;
                template = Mustache.to_html(template, {"info": "Print aborted"});
                document.getElementById("alert-buttons").innerHTML = template;

                template = document.getElementById("info-template").innerHTML;
                template = Mustache.to_html(template, {"info": "Select the svg slices"});
                document.getElementById("alert-upload").innerHTML = template;

                enable_button("start-button", true);
            }
            else {
                template = document.getElementById("error-template").innerHTML;
                template = Mustache.to_html(template, abortresponse);
                document.getElementById("alert-buttons").innerHTML = template;

                enable_button("start-button", true);
            }
        }
    };
    abortRequest.send();
};

update_status();