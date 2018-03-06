function enable_button(id, enable){
    button = document.getElementById(id);
    if (enable) {
        document.getElementById("start-button").removeAttribute("disabled");
    }
    else{
	if (!button.hasAttribute('disabled')){
            button.setAttribute('disabled', '');
	}
    }

}

UIkit.upload('#upload-svg', {

    url: '/upload',
    allow: '*.svg',

    completeAll: function (e) {
        //here is the response !!
	response = JSON.parse(e.response);
	
	if (response.valid){
            var template = document.getElementById("success-template").innerHTML;
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
    enable_button("upload-button", false);

    form = document.getElementById("input-svg");
    if (!form.hasAttribute('hidden')){
        form.setAttribute('hidden', '');
    }

    
};

document.getElementById("abort-button").onclick=function (){
    console.log('abort');
};
