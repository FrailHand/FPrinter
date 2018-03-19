function enable_button(id, enable){
    button = document.getElementById(id);
    if (enable) {
        button.removeAttribute("disabled");
    }
    else{
        if (!button.hasAttribute('disabled')){
                button.setAttribute('disabled', '');
        }
    }

}

function enable_upload(enable){
    enable_button("upload-button", enable);

    form = document.getElementById("input-svg");
    if(enable){
        form.removeAttribute("hidden");
    }
    else{
        if (!form.hasAttribute('hidden')){
            form.setAttribute('hidden', '');
        }
    }
}

UIkit.upload('#upload-svg', {

    url: '/upload',
    allow: '*.svg',

    completeAll: function (e) {
	response = JSON.parse(e.response);
	
	if (response.valid){
            var template = document.getElementById("file-success-template").innerHTML;
	    template = Mustache.to_html(template, response);
            document.getElementById("alert-upload").innerHTML = template;

	    enable_button('start-button', true);
        }
	else{
	    var template = document.getElementById("error-template").innerHTML;
	    template = Mustache.to_html(template, response);
            document.getElementById("alert-upload").innerHTML = template;

            enable_button('start-button', false);
	}
    },

    loadStart: function (e) {
	bar=document.getElementById("js-progressbar");

        var template = document.getElementById("progress-template").innerHTML;
        document.getElementById("alert-upload").innerHTML = template;

	if (bar !== null){
            bar.max = e.total;
            bar.value = e.loaded;
	}
    },

    progress: function (e) {
	bar=document.getElementById("js-progressbar");
        bar.max = e.total;
        bar.value = e.loaded;
    },
    
    fail: function () {
        enable_button('start-button', false);

	alert_element = document.getElementById("alert-invalid");
        if(alert_element == null){
            var template = document.getElementById("invalid-template").innerHTML;
            document.getElementById("alert-upload").innerHTML = template;
        }
	
        else {
            alert_element.classList.remove("uk-animation-shake");
            void alert_element.offsetWidth;
            alert_element.classList.add("uk-animation-shake");
        }

    }

    });

document.getElementById("start-button").onclick=function (){
    enable_upload(false);

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', "/button/start", true);
    xmlHttp.open('GET', "/button/start", true);

    xmlHttp.onreadystatechange = function() {

        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var response = JSON.parse(xmlHttp.response);

            if (response.valid){
                var template = document.getElementById("info-template").innerHTML;
	            template = Mustache.to_html(template,  {"info":"Printing in progress..."});
                document.getElementById("alert-buttons").innerHTML = template;

                enable_button('start-button', false);
                enable_button('pause-button', true);
                enable_button('abort-button', true);

            }
            else{
                var template = document.getElementById("error-template").innerHTML;
	            template = Mustache.to_html(template, response);
                document.getElementById("alert-buttons").innerHTML = template;

                enable_upload(true);
            }

        }
    }

    xmlHttp.send(null);

    
};

document.getElementById("abort-button").onclick=function (){
    console.log('abort');
};
