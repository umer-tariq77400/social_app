// Infinite scroll script for image listings
let page = 1;
let emptyPage = false;
let blockRequest = false;

window.addEventListener('scroll', function (e) {
    const margin = document.body.clientHeight - window.innerHeight - 200;
    if (window.pageYOffset > margin && !blockRequest && !emptyPage) {
        blockRequest = true;
        page += 1;

        // Show skeleton loader
        const imageList = document.getElementById("image-list");
        const skeletonTemplate = document.getElementById("skeleton-template");
        if (skeletonTemplate) {
            imageList.insertAdjacentHTML("beforeend", skeletonTemplate.innerHTML);
        }

        fetch(`?images_only=1&page=${page}`)
            .then(response => response.text())
            .then(html => {
                // Remove skeleton loader
                const skeletons = imageList.querySelectorAll(".skeleton-item");
                skeletons.forEach(el => el.remove());

                if (html.trim().length == 0) {
                    emptyPage = true;
                } else {
                    imageList.insertAdjacentHTML("beforeend", html);
                    blockRequest = false;
                }
            })
            .catch(error => {
                console.error("Infinite scroll fetch failed:", error);
                
                // Remove skeleton loader
                const skeletons = imageList.querySelectorAll(".skeleton-item");
                skeletons.forEach(el => el.remove());

                blockRequest = false; // Allow retry on error
            });
    }
});

// Trigger an initial scroll event to load more if needed
const scrollEvent = new Event('scroll');
window.dispatchEvent(scrollEvent);
