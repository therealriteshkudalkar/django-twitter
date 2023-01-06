function onFollowButtonClick() {
    let form = document.querySelector(".main-section__follow-form");

    let url = form.action;

    let follow_value = form.querySelector("input[name='follow_value']");
    let follower = form.querySelector("input[name='follower']");
    let profile = form.querySelector("input[name='profile']");
    let csrfmiddlewaretoken = form.querySelector("input[name='csrfmiddlewaretoken']").value;
    
    let data = new FormData();
    data.append('follower', follower.value);
    data.append('followee', profile.value);
    data.append('follow_value', follow_value.value);
    data.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

    fetch(url, {
        method: "POST",
        body: data,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        //perform operation with data
        if (data["response"] === "successful") {
            // check if follow was performed
            if (follow_value.value === 'Unfollow') {
                // Change button to follow
                follow_value.value = 'Follow'
                follow_value.classList.remove("main-section__unfollow")
            } else {
                follow_value.value = 'Unfollow'
                follow_value.classList.add("main-section__unfollow")
            }
        } else if (data["response"] === "login") {
            // show modal asking user to login
            let modal = document.getElementById("");
        } else {
            // show a modal showing error occurred
            let modal = document.getElementById("");
        }
    });
}

function showTweetModal() {
    const backdrop = document.getElementsByClassName("modal-backdrop")[0];
    backdrop.classList.add("show");
    backdrop.classList.remove("hide");
    const tweetModal = document.getElementsByClassName("modal-tweet")[0];
    tweetModal.classList.add("show");
    tweetModal.classList.remove("hide");
}

function dismissTweetModal() {
    const backdrop = document.getElementsByClassName("modal-backdrop")[0];
    backdrop.classList.add("hide");
    backdrop.classList.remove("show");
    const tweetModal = document.getElementsByClassName("modal-tweet")[0];
    tweetModal.classList.add("hide");
    tweetModal.classList.remove("show");
}

function showErrorModal() {
    // dismiss the modal which is visible
}

function showLoginModal() {
    // dismiss the modal which is visible
}