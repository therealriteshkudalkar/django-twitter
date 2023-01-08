function onRetweetButtonClick(context, tweet_id) {
    let retweetImage = context;
    let form = context.parentElement.parentElement;
    let retweetCount = form.querySelector(".single-tweet__retweet-count");

    let retweetImageUrl = form.querySelector("input[name='retweet_image_url']").value;
    let retweetedImageUrl = form.querySelector("input[name='retweeted_image_url']").value;

    let url = form.action;
    let retweetValue = form.querySelector("input[name='retweet_value']");
    let csrfmiddlewaretoken = form.querySelector("input[name='csrfmiddlewaretoken']").value;
    
    let data = new FormData();
    data.append('tweet_id', tweet_id);
    data.append('retweet_value', retweetValue.value);
    data.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

    // console.log(url, retweetValue, csrfmiddlewaretoken);

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
            if (retweetValue.value === 'Retweeted') {
                // Change button to follow
                retweetValue.value = 'Not retweeted';
                retweetImage.src = retweetImageUrl;
            } else {
                retweetValue.value = 'Retweeted';
                retweetImage.src = retweetedImageUrl;
            }
            retweetCount.innerHTML = data["count"];
        } else if (data["response"] === "login") {
            // show modal asking user to login
            showLoginModal();
        } else {
            // show a modal showing error occurred
            showErrorModal(data["response_message"]);
        }
    });
}

function onLikeButtonClick(context, tweet_id) {
    let likeImage = context;
    let form = context.parentElement.parentElement;
    let likeCount = form.querySelector(".single-tweet__like-count");

    let likeImageUrl = form.querySelector("input[name='like_image_url']").value;
    let likedImageUrl = form.querySelector("input[name='liked_image_url']").value;

    let url = form.action;
    let like_value = form.querySelector("input[name='like_value']");
    let csrfmiddlewaretoken = form.querySelector("input[name='csrfmiddlewaretoken']").value;
    
    let data = new FormData();
    data.append('tweet_id', tweet_id);
    data.append('like_value', like_value.value);
    data.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

    // console.log(url, like_value, csrfmiddlewaretoken);

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
            if (like_value.value === 'Liked') {
                // Change button to follow
                like_value.value = 'Not liked';
                likeImage.src = likeImageUrl;
            } else {
                like_value.value = 'Liked';
                likeImage.src = likedImageUrl;
            }
            likeCount.innerHTML = data["count"];
        } else if (data["response"] === "login") {
            // show modal asking user to login
            showLoginModal();
        } else {
            // show a modal showing error occurred
            showErrorModal(data["response_message"]);
        }
    });
}

function onDeleteTweetButtonClick() {
    //
}

function onBookmarkTweetButtonClick() {
    //
}

function showMoreTweetOptionModal(context, tweet_id) {
    const contextParent = context.parentElement;
    const modal = contextParent.querySelector(".single-tweet__more-options");
    modal.style.display = "block";
}

function dismissMoreTweetOptionModal(context, tweet_id) {
    const modal = context.parentElement.parentElement;
    modal.style.display = "none";
}