// Scroll to bottom when loaded
let messagesContainer = document.querySelector(".main-section__includer");
messagesContainer.scrollTo(0, messagesContainer.scrollHeight);

function messageTemplate(isSender, message, strTime) {
    return new String(`
    <div class="single-message single-message ` + (isSender ? 'single-message--blue' : '') + `">
        <div class="single-message__body ` + (isSender ? 'single-message__body--blue ' : '') + `">
            <p class="single-message__body-text ` + (isSender ? 'single-message__body-text--blue' : '') + `">` + message + `</p>
            <p class="single-message__body-date ` + (isSender ? 'single-message__body-date--blue' : '') + `">` + strTime + `</p>
        </div>
    </div>`)
}


function onSubmitMessage(context, userId) {
    let form = document.querySelector(".main-section__message-form");
    let parentContainer = document.querySelector(".main-section__includer");

    let url = form.action;
    let message = form.querySelector("input[name='message']");
    let csrfmiddlewaretoken = form.querySelector("input[name='csrfmiddlewaretoken']").value;

    let data = new FormData();
    data.append('message', message.value);
    data.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

    fetch(url, {
        method: "POST",
        body: data,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        //perform operation with data
        if (data["response"] === "successful") {
            // check if follow was performed
            let date = new Date();
            let hours = date.getHours();
            if (hours > 12) {
                var amPm = "p.m.";
                hours -= 12;
            } else {
                var amPm = "a.m.";
            }
            let strDate = date.getHours() + ":" + date.getMinutes() + " " + amPm;
            parentContainer.insertAdjacentHTML('beforeend', messageTemplate(true, message.value, strDate));
            message.value = "";
            parentContainer.scrollTo(0, parentContainer.scrollHeight);
        } else if (data["response"] === "login") {
            // show modal asking user to login
            showLoginModal();
        } else {
            // show a modal showing error occurred
            showErrorModal(data["response_message"], "Error");
        }
    });
}