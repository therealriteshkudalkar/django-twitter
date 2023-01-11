function selectTab(selection) {
    const tabLinks = document.querySelector(".main-section__heads").children;
    const followingTabLink = tabLinks[0];
    const followersTabLink = tabLinks[1];
    console.log(tabLinks, followingTabLink, followersTabLink);
    const followingTab = document.querySelector(".main-section__following");
    const followersTab = document.querySelector(".main-section__followers");

    if (selection === 'following') {
        // show tweetTab
        followingTab.style.display = "block";
        followersTab.style.display = "none";
        followingTabLink.classList.add("main-section__heads-item--selected");
        followersTabLink.classList.remove("main-section__heads-item--selected");
    } else {
        // show likeTab
        followingTab.style.display = "none";
        followersTab.style.display = "block";
        followingTabLink.classList.remove("main-section__heads-item--selected");
        followersTabLink.classList.add("main-section__heads-item--selected");
    }
}

function onFollowButtonClick(context, username) {

    let form = context.parentElement;

    let url = form.action;

    let follow_value = form.querySelector(".follow-item__follow-button");
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
        //perform operation with data
        if (data["response"] === "successful") {
            // check if follow was performed
            if (follow_value.innerHTML === 'Following') {
                // Change button to follow
                follow_value.innerHTML = 'Follow'
                follow_value.classList.remove("follow-item__follow-button--following")
            } else {
                follow_value.innerHTML = 'Following'
                follow_value.classList.add("follow-item__follow-button--following")
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