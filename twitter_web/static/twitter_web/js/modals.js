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

function showErrorModal(message, title) {
    const backdrop = document.getElementsByClassName("modal-backdrop")[0];
    backdrop.classList.add("show");
    backdrop.classList.remove("hide");

    const errorModal = document.getElementsByClassName("modal-error")[0];
    errorModal.classList.add("show");
    errorModal.classList.remove("hide");

    const headTag = errorModal.getElementsByClassName("modal-error__head")[0];
    headTag.innerHTML = title;
    const messageTag = errorModal.getElementsByClassName("modal-error__message")[0];
    messageTag.innerHTML = message;
}

function dismissErrorModal() {
    const backdrop = document.getElementsByClassName("modal-backdrop")[0];
    backdrop.classList.add("hide");
    backdrop.classList.remove("show");

    const errorModal = document.getElementsByClassName("modal-error")[0];
    errorModal.classList.add("hide");
    errorModal.classList.remove("show");
}

function showLoginModal() {
    const backdrop = document.getElementsByClassName("modal-backdrop")[0];
    backdrop.classList.add("show");
    backdrop.classList.remove("hide");

    const tweetModal = document.getElementsByClassName("modal-login")[0];
    tweetModal.classList.add("show");
    tweetModal.classList.remove("hide");
}

function dismissLoginModal() {
    const backdrop = document.getElementsByClassName("modal-backdrop")[0];
    backdrop.classList.add("hide");
    backdrop.classList.remove("show");

    const tweetModal = document.getElementsByClassName("modal-login")[0];
    tweetModal.classList.add("hide");
    tweetModal.classList.remove("show");
}