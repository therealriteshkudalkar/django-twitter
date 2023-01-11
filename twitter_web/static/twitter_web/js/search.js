function onTabSelection(selection) {
    const tabLinks = document.querySelector(".tab-links").children;

    const latestTweetsTabLink = tabLinks[0];
    const trendsTabLink = tabLinks[1];
    const peopleTabLink = tabLinks[2];
    
    const latestTweetsTab = document.querySelector(".latest-tweets");
    const trendsTab = document.querySelector(".trending");
    const peoplesTab = document.querySelector(".people");

    if (selection === 'latest-tweets') {
        // show tweetTab
        latestTweetsTab.style.display = "block";
        trendsTab.style.display = "none";
        peoplesTab.style.display = "none";
        latestTweetsTabLink.classList.add("tab-link__item--selected");
        trendsTabLink.classList.remove("tab-link__item--selected");
        peopleTabLink.classList.remove("tab-link__item--selected");
    } else if (selection === 'trending') {
        // show likeTab
        latestTweetsTab.style.display = "none";
        trendsTab.style.display = "block";
        peoplesTab.style.display = "none";
        latestTweetsTabLink.classList.remove("tab-link__item--selected");
        trendsTabLink.classList.add("tab-link__item--selected");
        peopleTabLink.classList.remove("tab-link__item--selected");
    } else {
        latestTweetsTab.style.display = "none";
        trendsTab.style.display = "none";
        peoplesTab.style.display = "block";
        latestTweetsTabLink.classList.remove("tab-link__item--selected");
        trendsTabLink.classList.remove("tab-link__item--selected");
        peopleTabLink.classList.add("tab-link__item--selected");
    }
}
