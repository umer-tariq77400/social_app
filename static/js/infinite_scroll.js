// Infinite scroll script for image listings
let page = 1;
let emptyPage = false;
let blockRequest = false;

window.addEventListener('scroll', function (e) {
    const margin = document.body.clientHeight - window.innerHeight - 200;
    if (window.pageYOffset > margin && !blockRequest && !emptyPage) {
        blockRequest = true;
        page += 1;
        fetch(`?images_only=1&page=${page}`)
            .then(response => response.text())
            .then(html => {
                if (html.trim().length == 0) {
                    emptyPage = true;
                } else {
                    document.getElementById("image-list").insertAdjacentHTML("beforeend", html);
                    blockRequest = false;
                }
            })
            .catch(error => {
                console.error("Infinite scroll fetch failed:", error);
                blockRequest = false; // Allow retry on error
            });
    }
});

// Trigger an initial scroll event to load more if needed
const scrollEvent = new Event('scroll');
window.dispatchEvent(scrollEvent);
