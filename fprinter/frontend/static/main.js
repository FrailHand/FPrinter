UIkit.upload('#upload-zip', {

    url: '/upload',
    allow: '*.zip',

    completeAll: function (e) {
        //here is the response !!
        console.log(e);

        if(document.getElementById('alert-invalid') !== null){
            UIkit.alert('#alert-invalid').close();
        }

        alert_element = document.getElementById('alert-success');
        var template = document.getElementById("success-template").innerHTML;
        var node = document.createElement('div');
        node.innerHTML = template;
        document.getElementById("upload-panel").appendChild(node.firstElementChild);
        if(alert_element !== null){
            document.getElementById("upload-panel").removeChild(alert_element);
            }

        document.getElementById("start-button").removeAttribute("disabled");
    },
    fail: function () {
        start_but = document.getElementById('start-button');
        if (!start_but.hasAttribute('disabled')){
            start_but.setAttribute('disabled', '');
        }
        if(document.getElementById('alert-success') !== null){
            UIkit.alert('#alert-success').close();
        }

        alert_element = document.getElementById('alert-invalid');
        if(alert_element == null){
            var template = document.getElementById("invalid-template").innerHTML;
            var node = document.createElement('div');
            node.innerHTML = template;
            document.getElementById("upload-panel").appendChild(node.firstElementChild);
        }
        else {
            alert_element.classList.remove("uk-animation-shake");
            void alert_element.offsetWidth;
            alert_element.classList.add("uk-animation-shake");
        }

    }

    });