/* working of tabs */

function selectTab(selection) {
    const tabLinks = document.querySelector(".main-section__tab-links").children;
    const tweetTabLink = tabLinks[0];
    const likeTabLink = tabLinks[1];
    console.log(tabLinks, tweetTabLink, likeTabLink);
    const tweetTab = document.querySelector(".main-section__tweets");
    const likeTab = document.querySelector(".main-section__liked-tweets");

    if (selection === 'tweets') {
        // show tweetTab
        tweetTab.style.display = "block";
        likeTab.style.display = "none";
        tweetTabLink.classList.add("main-section__tab-link--selected");
        likeTabLink.classList.remove("main-section__tab-link--selected");
    } else {
        // show likeTab
        tweetTab.style.display = "none";
        likeTab.style.display = "block";
        tweetTabLink.classList.remove("main-section__tab-link--selected");
        likeTabLink.classList.add("main-section__tab-link--selected");
    }
}


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
            showLoginModal();
        } else {
            // show a modal showing error occurred
            showErrorModal(data["response_message"], "Error");
        }
    });
}
